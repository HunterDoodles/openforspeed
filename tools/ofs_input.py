#!/usr/bin/env python3
"""OpenForSpeed input tool. Standard library only, no root needed."""

import argparse
import ctypes
import fcntl
import glob
import json
import os
import select
import struct
import sys
import time

CONFIG_DIR = os.path.expanduser('~/.config/openforspeed')
PROFILE_DIR = os.path.join(CONFIG_DIR, 'input')

EV_SYN, EV_KEY, EV_ABS = 0x00, 0x01, 0x03
SYN_REPORT = 0
BUS_USB = 0x03

EVIOCGRAB = 0x40044590
UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_SET_ABSBIT = 0x40045567
UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502

EVENT_FORMAT = 'llHHi'
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

AXIS_NAMES = {
    0x00: 'X', 0x01: 'Y', 0x02: 'Z',
    0x03: 'RX', 0x04: 'RY', 0x05: 'RZ',
    0x06: 'THROTTLE', 0x07: 'RUDDER', 0x08: 'WHEEL',
    0x09: 'GAS', 0x0a: 'BRAKE',
    0x10: 'HAT0X', 0x11: 'HAT0Y',
}

ROLE_HINTS = {
    'X': 'steering', 'Y': 'pedal', 'Z': 'pedal', 'RZ': 'pedal',
    'RX': 'pedal', 'RY': 'pedal', 'HAT0X': 'dpad', 'HAT0Y': 'dpad',
}


class AbsInfo(ctypes.Structure):
    _fields_ = [('value', ctypes.c_int32), ('minimum', ctypes.c_int32),
                ('maximum', ctypes.c_int32), ('fuzz', ctypes.c_int32),
                ('flat', ctypes.c_int32), ('resolution', ctypes.c_int32)]


class UinputUserDev(ctypes.Structure):
    _fields_ = [('name', ctypes.c_char * 80),
                ('bustype', ctypes.c_uint16), ('vendor', ctypes.c_uint16),
                ('product', ctypes.c_uint16), ('version', ctypes.c_uint16),
                ('ff_effects_max', ctypes.c_uint32),
                ('absmax', ctypes.c_int32 * 64), ('absmin', ctypes.c_int32 * 64),
                ('absfuzz', ctypes.c_int32 * 64), ('absflat', ctypes.c_int32 * 64)]


def eviocgabs(code):
    return 0x80184540 + code


def eviocgname(length):
    return 0x80004506 + (length << 16)


def eviocgbit(ev, length):
    return 0x80004520 + ev + (length << 16)


def device_name(fd):
    buf = ctypes.create_string_buffer(256)
    try:
        fcntl.ioctl(fd, eviocgname(256), buf)
    except OSError:
        return 'unknown'
    return buf.value.decode('utf-8', 'replace')


def supported_codes(fd, ev_type, limit):
    size = (limit + 7) // 8
    buf = ctypes.create_string_buffer(size)
    try:
        fcntl.ioctl(fd, eviocgbit(ev_type, size), buf)
    except OSError:
        return []
    out = []
    for code in range(limit):
        if buf.raw[code // 8] & (1 << (code % 8)):
            out.append(code)
    return out


def list_devices():
    found = []
    for path in sorted(glob.glob('/dev/input/event*')):
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        except OSError:
            continue
        name = device_name(fd)
        axes = supported_codes(fd, EV_ABS, 0x40)
        buttons = supported_codes(fd, EV_KEY, 0x300)
        os.close(fd)
        if axes and buttons:
            found.append({'path': path, 'name': name,
                          'axes': axes, 'buttons': buttons})
    return found


def read_axis(fd, code):
    info = AbsInfo()
    try:
        fcntl.ioctl(fd, eviocgabs(code), info)
    except OSError:
        return None
    return info


def looks_like_wheel(name):
    low = name.lower()
    return any(k in low for k in ('wheel', 'racing', 'g29', 'g27', 'g25', 'driving'))


def pick_device(prefer=None):
    devices = list_devices()
    if not devices:
        return None
    if prefer == 'wheel':
        for dev in devices:
            if looks_like_wheel(dev['name']):
                return dev
    if prefer == 'gamepad':
        for dev in devices:
            if not looks_like_wheel(dev['name']):
                return dev
    return devices[0]


def default_profile(dev):
    fd = os.open(dev['path'], os.O_RDONLY | os.O_NONBLOCK)
    axes = {}
    for code in dev['axes']:
        info = read_axis(fd, code)
        if info is None or info.maximum == info.minimum:
            continue
        span = info.maximum - info.minimum
        centre = (info.minimum + info.maximum) / 2
        offset = abs(info.value - centre) / span
        name = AXIS_NAMES.get(code, 'AXIS%d' % code)
        axes[str(code)] = {
            'name': name,
            'role': ROLE_HINTS.get(name, 'other'),
            'min': info.minimum,
            'max': info.maximum,
            'rest': info.value,
            'deadzone': 0.10 if name == 'X' else 0.0,
            'invert': False,
            'enabled': not (offset > 0.4 and ROLE_HINTS.get(name) == 'pedal'),
        }
    os.close(fd)
    return {'device': dev['name'], 'axes': axes,
            'buttons': dev['buttons'], 'bindings': {}}


def profile_path(name):
    return os.path.join(PROFILE_DIR, name + '.json')


def save_profile(name, profile):
    os.makedirs(PROFILE_DIR, exist_ok=True)
    with open(profile_path(name), 'w') as handle:
        json.dump(profile, handle, indent=2)


def load_profile(name):
    try:
        with open(profile_path(name)) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def bar(value, low, high, width=32):
    if high == low:
        return ' ' * width
    pos = int((value - low) / (high - low) * (width - 1))
    pos = max(0, min(width - 1, pos))
    cells = ['.'] * width
    cells[width // 2] = '|'
    cells[pos] = '#'
    return ''.join(cells)


def monitor(dev, profile, seconds=None):
    fd = os.open(dev['path'], os.O_RDONLY | os.O_NONBLOCK)
    values = {}
    for code_str in profile['axes']:
        info = read_axis(fd, int(code_str))
        if info:
            values[int(code_str)] = info.value
    pressed = set()
    start = time.time()
    lines_drawn = 0
    try:
        while seconds is None or time.time() - start < seconds:
            ready, _, _ = select.select([fd], [], [], 0.05)
            if ready:
                try:
                    data = os.read(fd, EVENT_SIZE * 64)
                except BlockingIOError:
                    data = b''
                for i in range(0, len(data) - EVENT_SIZE + 1, EVENT_SIZE):
                    _s, _u, etype, code, value = struct.unpack(
                        EVENT_FORMAT, data[i:i + EVENT_SIZE])
                    if etype == EV_ABS:
                        values[code] = value
                    elif etype == EV_KEY:
                        if value:
                            pressed.add(code)
                        else:
                            pressed.discard(code)
            if lines_drawn:
                sys.stdout.write('\033[%dA' % lines_drawn)
            lines_drawn = 0
            for code_str, axis in sorted(profile['axes'].items(), key=lambda kv: int(kv[0])):
                code = int(code_str)
                raw = values.get(code, axis['rest'])
                out = apply_axis(axis, raw)
                state = 'ON ' if axis['enabled'] else 'off'
                flag = 'INV' if axis['invert'] else '   '
                print('  %-8s %s %s [%s] raw=%-6d out=%+.2f\033[K'
                      % (axis['name'], state, flag, bar(out, -1.0, 1.0), raw, out))
                lines_drawn += 1
            btns = ' '.join(str(b) for b in sorted(pressed)) or '-'
            print('  buttons: %s\033[K' % btns)
            lines_drawn += 1
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        os.close(fd)
    print()


def apply_axis(axis, raw):
    low, high = axis['min'], axis['max']
    if high == low:
        return 0.0
    rest = axis.get('rest', (low + high) / 2)
    if raw >= rest:
        span = high - rest
        norm = (raw - rest) / span if span else 0.0
    else:
        span = rest - low
        norm = (raw - rest) / span if span else 0.0
    dead = axis.get('deadzone', 0.0)
    if dead > 0:
        if abs(norm) <= dead:
            norm = 0.0
        else:
            norm = (abs(norm) - dead) / (1 - dead) * (1 if norm > 0 else -1)
    if axis.get('invert'):
        norm = -norm
    return max(-1.0, min(1.0, norm))


def capture_button(dev, prompt, timeout=10):
    fd = os.open(dev['path'], os.O_RDONLY | os.O_NONBLOCK)
    print('  %s ' % prompt, end='', flush=True)
    end = time.time() + timeout
    result = None
    while time.time() < end and result is None:
        ready, _, _ = select.select([fd], [], [], 0.1)
        if not ready:
            continue
        try:
            data = os.read(fd, EVENT_SIZE * 64)
        except BlockingIOError:
            continue
        for i in range(0, len(data) - EVENT_SIZE + 1, EVENT_SIZE):
            _s, _u, etype, code, value = struct.unpack(
                EVENT_FORMAT, data[i:i + EVENT_SIZE])
            if etype == EV_KEY and value == 1:
                result = code
                break
    os.close(fd)
    print('button %s' % result if result is not None else 'skipped')
    return result


class VirtualDevice:
    def __init__(self, name, axes, buttons):
        self.fd = os.open('/dev/uinput', os.O_WRONLY | os.O_NONBLOCK)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_KEY)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_ABS)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_SYN)
        for code in buttons:
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, code)
        for code in axes:
            fcntl.ioctl(self.fd, UI_SET_ABSBIT, code)
        setup = UinputUserDev()
        setup.name = name.encode()[:79]
        setup.bustype = BUS_USB
        setup.vendor = 0x046d
        setup.product = 0xc24f
        setup.version = 1
        for code in axes:
            setup.absmin[code] = -32767
            setup.absmax[code] = 32767
            setup.absfuzz[code] = 0
            setup.absflat[code] = 0
        os.write(self.fd, bytes(setup))
        fcntl.ioctl(self.fd, UI_DEV_CREATE)
        time.sleep(0.3)

    def emit(self, etype, code, value):
        now = time.time()
        packet = struct.pack(EVENT_FORMAT, int(now), int(now % 1 * 1e6),
                             etype, code, value)
        os.write(self.fd, packet)

    def sync(self):
        self.emit(EV_SYN, SYN_REPORT, 0)

    def close(self):
        try:
            fcntl.ioctl(self.fd, UI_DEV_DESTROY)
        except OSError:
            pass
        os.close(self.fd)


def run_bridge(dev, profile, grab=True):
    enabled = {int(c): a for c, a in profile['axes'].items() if a['enabled']}
    if not enabled:
        print('no axes enabled in this profile')
        return
    virtual = VirtualDevice('OpenForSpeed %s' % profile.get('device', 'Wheel'),
                            list(enabled.keys()), profile['buttons'])
    src = os.open(dev['path'], os.O_RDONLY)
    if grab:
        try:
            fcntl.ioctl(src, EVIOCGRAB, 1)
        except OSError:
            print('could not grab the real device, both will be visible')
    print('bridge running, the game should use "OpenForSpeed ..."')
    print('press ctrl-c to stop')
    try:
        while True:
            ready, _, _ = select.select([src], [], [], 0.5)
            if not ready:
                continue
            data = os.read(src, EVENT_SIZE * 64)
            dirty = False
            for i in range(0, len(data) - EVENT_SIZE + 1, EVENT_SIZE):
                _s, _u, etype, code, value = struct.unpack(
                    EVENT_FORMAT, data[i:i + EVENT_SIZE])
                if etype == EV_ABS and code in enabled:
                    out = apply_axis(enabled[code], value)
                    virtual.emit(EV_ABS, code, int(out * 32767))
                    dirty = True
                elif etype == EV_KEY:
                    virtual.emit(EV_KEY, code, value)
                    dirty = True
            if dirty:
                virtual.sync()
    except KeyboardInterrupt:
        pass
    finally:
        if grab:
            try:
                fcntl.ioctl(src, EVIOCGRAB, 0)
            except OSError:
                pass
        os.close(src)
        virtual.close()
        print('\nbridge stopped')


def cmd_list(args):
    for dev in list_devices():
        kind = 'wheel' if looks_like_wheel(dev['name']) else 'gamepad'
        print('%-8s %-40s %s' % (kind, dev['name'], dev['path']))
        fd = os.open(dev['path'], os.O_RDONLY | os.O_NONBLOCK)
        for code in dev['axes']:
            info = read_axis(fd, code)
            if not info or info.maximum == info.minimum:
                continue
            span = info.maximum - info.minimum
            centre = (info.minimum + info.maximum) / 2
            off = abs(info.value - centre) / span
            warn = '  <- rests off centre' if off > 0.4 else ''
            print('    %-8s %6d  (%d..%d)%s'
                  % (AXIS_NAMES.get(code, code), info.value,
                     info.minimum, info.maximum, warn))
        os.close(fd)
        print('    %d buttons' % len(dev['buttons']))


def cmd_calibrate(args):
    dev = pick_device(args.device)
    if not dev:
        print('no input device found')
        return 1
    profile = load_profile(args.profile) or default_profile(dev)
    print('device: %s' % dev['name'])
    print('profile: %s' % args.profile)
    print()
    print('move everything, then press ctrl-c to continue')
    print()
    monitor(dev, profile)
    for code_str, axis in sorted(profile['axes'].items(), key=lambda kv: int(kv[0])):
        print('%s (%s)' % (axis['name'], axis['role']))
        ans = input('  enable? [Y/n] ').strip().lower()
        axis['enabled'] = ans != 'n'
        if not axis['enabled']:
            continue
        ans = input('  invert? [y/N] ').strip().lower()
        axis['invert'] = ans == 'y'
        ans = input('  deadzone percent [%d] ' % int(axis['deadzone'] * 100)).strip()
        if ans.isdigit():
            axis['deadzone'] = min(90, int(ans)) / 100.0
    save_profile(args.profile, profile)
    print('\nsaved to %s' % profile_path(args.profile))
    return 0


def cmd_bridge(args):
    dev = pick_device(args.device)
    if not dev:
        print('no input device found')
        return 1
    profile = load_profile(args.profile)
    if not profile:
        print('no profile named %s, run calibrate first' % args.profile)
        return 1
    run_bridge(dev, profile, grab=not args.no_grab)
    return 0


def cmd_monitor(args):
    dev = pick_device(args.device)
    if not dev:
        print('no input device found')
        return 1
    profile = load_profile(args.profile) or default_profile(dev)
    monitor(dev, profile)
    return 0


def main():
    parser = argparse.ArgumentParser(description='OpenForSpeed input tool')
    sub = parser.add_subparsers(dest='command')

    p = sub.add_parser('list', help='show input devices and their axes')
    p.set_defaults(func=cmd_list)

    for name, func, helptext in (
            ('calibrate', cmd_calibrate, 'set deadzones, inversion and which axes to keep'),
            ('monitor', cmd_monitor, 'watch axes and buttons live'),
            ('bridge', cmd_bridge, 'expose a cleaned up virtual device')):
        p = sub.add_parser(name, help=helptext)
        p.add_argument('--device', choices=['wheel', 'gamepad'], default='wheel')
        p.add_argument('--profile', default='wheel')
        if name == 'bridge':
            p.add_argument('--no-grab', action='store_true',
                           help='leave the real device visible to games too')
        p.set_defaults(func=func)

    args = parser.parse_args()
    if not getattr(args, 'func', None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())

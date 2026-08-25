#!/usr/bin/env python3
"""OpenForSpeed input tool. Standard library only, no root needed."""

# The original version of this project by agentkyo has been vibe coded out the ass. 
# I want to restructure it from scratch, but it would take a ton of effort.
# So for now I decided to fork the project so that I would know from
# henceforth the project will have human-authored code in it.

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
EV_FF = 0x15
EV_UINPUT = 0x0101
SYN_REPORT = 0
BUS_USB = 0x03

FF_NAMES = {0x50: 'rumble', 0x51: 'periodic', 0x52: 'constant',
            0x53: 'spring', 0x54: 'friction', 0x55: 'damper',
            0x56: 'inertia', 0x57: 'ramp'}

UI_FF_UPLOAD = 1
UI_FF_ERASE = 2
FF_EFFECT_SIZE = 48

EVIOCGRAB = 0x40044590
UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_SET_ABSBIT = 0x40045567
UI_SET_FFBIT = 0x4004556b
UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502
UI_BEGIN_FF_UPLOAD = 0xc06855c8
UI_END_FF_UPLOAD = 0x406855c9
UI_BEGIN_FF_ERASE = 0xc00c55ca
UI_END_FF_ERASE = 0x400c55cb
EVIOCSFF = 0x40304580
EVIOCRMFF = 0x40044581

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


# The original version of Open for Speed didn't list any of the
# various axis-based inputs by their name. 
# I implemented this system to fix that.
AXIS_LABELS = {
    'X': 'Left Stick X (left/right)',
    'Y': 'Left Stick Y (up/down)',
    'Z': 'Left Trigger (L2 / LT)',
    'RX': 'Right Stick X (left/right)',
    'RY': 'Right Stick Y (up/down)',
    'RZ': 'Right Trigger (R2 / RT)',
    'THROTTLE': 'Throttle',
    'RUDDER': 'Rudder',
    'WHEEL': 'Steering Wheel',
    'GAS': 'Gas Pedal',
    'BRAKE': 'Brake Pedal',
    'HAT0X': 'D-Pad X (right=1, left=-1)',
    'HAT0Y': 'D-Pad Y (down=1, up=-1)',
}


def axis_label(short_name):
    return AXIS_LABELS.get(short_name, short_name)


# Same as for the above, but for buttons!
BUTTON_LABELS = {
    0x130: 'South (Cross / A)',
    0x131: 'East (Circle / B)',
    0x132: 'C',
    0x133: 'North (Triangle / Y)',
    0x134: 'West (Square / X)',
    0x135: 'Z',
    0x136: 'L1 / LB',
    0x137: 'R1 / RB',
    0x138: 'L2 / LT',
    0x139: 'R2 / RT',
    0x13a: 'Select (Create / Back)',
    0x13b: 'Start (Options / Start)',
    0x13c: 'Mode (PS / Guide)',
    0x13d: 'L3 (left stick click)',
    0x13e: 'R3 (right stick click)',
    0x220: 'D-Pad Up',
    0x221: 'D-Pad Down',
    0x222: 'D-Pad Left',
    0x223: 'D-Pad Right',
}


def button_label(code):
    return BUTTON_LABELS.get(code, 'button %d' % code)


# I had an issue getting the program to work with my controller
# due to it detecting my various graphics tablets (The kind for
# making art / drawing). So, I implemented a check for various
# graphics tablets and their accessories. I probably missed some,
# But they should be easy enough to add additional ones. As an
# added bonus, it's really easy to ignore any device at all
# just by adding the name to TABLET_NAME_HINTS so I might just
# restructure this to be for unwanted devices in general.
ABS_PRESSURE, ABS_TILT_X, ABS_TILT_Y = 0x18, 0x1a, 0x1b
TABLET_ABS_CODES = {ABS_PRESSURE, ABS_TILT_X, ABS_TILT_Y}
BTN_TOOL_PEN, BTN_TOOL_RUBBER, BTN_TOOL_BRUSH = 0x140, 0x141, 0x142
BTN_TOOL_PENCIL, BTN_TOOL_AIRBRUSH = 0x143, 0x144
BTN_TOUCH, BTN_STYLUS, BTN_STYLUS2 = 0x14a, 0x14b, 0x14c
TABLET_KEY_CODES = {BTN_TOOL_PEN, BTN_TOOL_RUBBER, BTN_TOOL_BRUSH,
                     BTN_TOOL_PENCIL, BTN_TOOL_AIRBRUSH, BTN_TOUCH,
                     BTN_STYLUS, BTN_STYLUS2}
TABLET_NAME_HINTS = ('huion', 'wacom', 'xp-pen', 'xppen', 'gaomon',
                     'veikk', 'ugee', 'tablet', 'pen display', 'pen tablet')


def looks_like_tablet(name, axes, buttons):
    if any(hint in name.lower() for hint in TABLET_NAME_HINTS):
        return True
    if TABLET_ABS_CODES & set(axes):
        return True
    if TABLET_KEY_CODES & set(buttons):
        return True
    return False


class AbsInfo(ctypes.Structure):
    _fields_ = [('value', ctypes.c_int32), ('minimum', ctypes.c_int32),
                ('maximum', ctypes.c_int32), ('fuzz', ctypes.c_int32),
                ('flat', ctypes.c_int32), ('resolution', ctypes.c_int32)]


class FFEffect(ctypes.Structure):
    _fields_ = [('raw', ctypes.c_ubyte * FF_EFFECT_SIZE)]

    @property
    def effect_id(self):
        return struct.unpack_from('h', bytes(self.raw), 2)[0]

    def set_id(self, value):
        data = bytearray(bytes(self.raw))
        struct.pack_into('h', data, 2, value)
        ctypes.memmove(self.raw, bytes(data), FF_EFFECT_SIZE)

    @property
    def effect_type(self):
        return struct.unpack_from('H', bytes(self.raw), 0)[0]

    def scale_strength(self, gain):
        if gain == 1.0:
            return
        data = bytearray(bytes(self.raw))
        kind = struct.unpack_from('H', data, 0)[0]
        offsets = []
        if kind == 0x52:
            offsets = [16]
        elif kind == 0x51:
            offsets = [20]
        elif kind == 0x57:
            offsets = [16, 18]
        elif kind == 0x50:
            offsets = []
        for off in offsets:
            level = struct.unpack_from('h', data, off)[0]
            level = int(max(-32767, min(32767, level * gain)))
            struct.pack_into('h', data, off, level)
        ctypes.memmove(self.raw, bytes(data), FF_EFFECT_SIZE)


class UinputFFUpload(ctypes.Structure):
    _fields_ = [('request_id', ctypes.c_uint32), ('retval', ctypes.c_int32),
                ('effect', FFEffect), ('old', FFEffect)]


class UinputFFErase(ctypes.Structure):
    _fields_ = [('request_id', ctypes.c_uint32), ('retval', ctypes.c_int32),
                ('effect_id', ctypes.c_uint32)]


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
        if axes and buttons and not looks_like_tablet(name, axes, buttons):
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
        role = ROLE_HINTS.get(name, 'other')
        rest = info.value
        if role in ('steering', 'dpad'):
            rest = (info.minimum + info.maximum) // 2
        axes[str(code)] = {
            'name': name,
            'role': role,
            'min': info.minimum,
            'max': info.maximum,
            'rest': rest,
            'deadzone': 0.02 if role == 'steering' else 0.0,
            'invert': False,
            'enabled': not (offset > 0.4 and role == 'pedal'),
        }
    os.close(fd)
    return {'device': dev['name'], 'axes': axes,
            'buttons': dev['buttons'], 'bindings': {}, 'ff_gain': 1.0}


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
                print('  %-8s %-28s %s %s [%s] raw=%-6d out=%+.2f\033[K'
                      % (axis['name'], axis_label(axis['name']), state, flag,
                         bar(out, -1.0, 1.0), raw, out))
                lines_drawn += 1
            btns = ', '.join(button_label(b) for b in sorted(pressed)) or '-'
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
    print(button_label(result) if result is not None else 'skipped')
    return result


class VirtualDevice:
    def __init__(self, name, axes, buttons, ff_effects=(), ff_max=0):
        flags = os.O_RDWR if ff_effects else os.O_WRONLY
        self.fd = os.open('/dev/uinput', flags | os.O_NONBLOCK)
        self.ff_effects = list(ff_effects)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_KEY)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_ABS)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_SYN)
        for code in buttons:
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, code)
        for code in axes:
            fcntl.ioctl(self.fd, UI_SET_ABSBIT, code)
        if self.ff_effects:
            fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_FF)
            for code in self.ff_effects:
                fcntl.ioctl(self.fd, UI_SET_FFBIT, code)
        setup = UinputUserDev()
        setup.name = name.encode()[:79]
        setup.bustype = BUS_USB
        setup.vendor = 0x046d
        setup.product = 0xc24f
        setup.version = 1
        setup.ff_effects_max = ff_max
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


def real_device_ff(path):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    except OSError:
        return []
    codes = supported_codes(fd, EV_FF, 0x80)
    os.close(fd)
    return [c for c in codes if c in FF_NAMES]


def handle_ff_request(virtual, real_fd, event_code, id_map, gain=1.0):
    if event_code == UI_FF_UPLOAD:
        request = UinputFFUpload()
        request.request_id = 0
        try:
            fcntl.ioctl(virtual.fd, UI_BEGIN_FF_UPLOAD, request)
        except OSError:
            return
        virtual_id = request.effect.effect_id
        forwarded = FFEffect()
        ctypes.memmove(forwarded.raw, request.effect.raw, FF_EFFECT_SIZE)
        forwarded.scale_strength(gain)
        forwarded.set_id(id_map.get(virtual_id, -1))
        try:
            fcntl.ioctl(real_fd, EVIOCSFF, forwarded)
            id_map[virtual_id] = forwarded.effect_id
            request.retval = 0
        except OSError:
            request.retval = -1
        try:
            fcntl.ioctl(virtual.fd, UI_END_FF_UPLOAD, request)
        except OSError:
            pass
    elif event_code == UI_FF_ERASE:
        request = UinputFFErase()
        try:
            fcntl.ioctl(virtual.fd, UI_BEGIN_FF_ERASE, request)
        except OSError:
            return
        real_id = id_map.pop(request.effect_id, None)
        request.retval = 0
        if real_id is not None:
            try:
                fcntl.ioctl(real_fd, EVIOCRMFF, real_id)
            except OSError:
                request.retval = -1
        try:
            fcntl.ioctl(virtual.fd, UI_END_FF_ERASE, request)
        except OSError:
            pass


LOCK_PATH = os.path.join(CONFIG_DIR, 'bridge.lock')


def acquire_lock():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    handle = open(LOCK_PATH, 'w')
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        return None
    handle.write(str(os.getpid()))
    handle.flush()
    return handle


def run_bridge(dev, profile, grab=True):
    lock = acquire_lock()
    if lock is None:
        print('a bridge is already running, leaving it alone')
        return
    enabled = {int(c): a for c, a in profile['axes'].items() if a['enabled']}
    if not enabled:
        print('no axes enabled in this profile')
        return
    ff_codes = real_device_ff(dev['path'])
    virtual = VirtualDevice('OpenForSpeed %s' % profile.get('device', 'Wheel'),
                            list(enabled.keys()), profile['buttons'],
                            ff_effects=ff_codes, ff_max=16 if ff_codes else 0)
    if ff_codes:
        print('force feedback forwarded: %s'
              % ', '.join(FF_NAMES[c] for c in ff_codes))
    try:
        src = os.open(dev['path'], os.O_RDWR if ff_codes else os.O_RDONLY)
    except OSError:
        src = os.open(dev['path'], os.O_RDONLY)
        ff_codes = []
    if grab:
        try:
            fcntl.ioctl(src, EVIOCGRAB, 1)
        except OSError:
            print('could not grab the real device, both will be visible')
    print('bridge running, the game should use "OpenForSpeed ..."')
    print('press ctrl-c to stop')
    id_map = {}
    ff_gain = float(profile.get('ff_gain', 1.0))
    if ff_codes and ff_gain != 1.0:
        print('force feedback strength: %d%%' % int(ff_gain * 100))
    watch = [src, virtual.fd] if ff_codes else [src]
    try:
        while True:
            ready, _, _ = select.select(watch, [], [], 0.5)
            if virtual.fd in ready:
                try:
                    blob = os.read(virtual.fd, EVENT_SIZE * 16)
                except (BlockingIOError, OSError):
                    blob = b''
                for i in range(0, len(blob) - EVENT_SIZE + 1, EVENT_SIZE):
                    _s, _u, etype, code, value = struct.unpack(
                        EVENT_FORMAT, blob[i:i + EVENT_SIZE])
                    if etype == EV_UINPUT:
                        handle_ff_request(virtual, src, code, id_map, ff_gain)
                    elif etype == EV_FF:
                        real_id = id_map.get(code, code)
                        now = time.time()
                        os.write(src, struct.pack(
                            EVENT_FORMAT, int(now), int(now % 1 * 1e6),
                            EV_FF, real_id, value))
            if src not in ready:
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
            name = AXIS_NAMES.get(code, code)
            print('    %-8s %-28s %6d  (%d..%d)%s'
                  % (name, axis_label(name) if isinstance(name, str) else '',
                     info.value, info.minimum, info.maximum, warn))
        os.close(fd)
        btn_names = [button_label(c) for c in sorted(dev['buttons'])
                     if c in BUTTON_LABELS]
        print('    %d buttons%s' % (len(dev['buttons']),
              ': ' + ', '.join(btn_names) if btn_names else ''))


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
        print('%s — %s (%s)' % (axis['name'], axis_label(axis['name']), axis['role']))
        ans = input('  enable? [Y/n] ').strip().lower()
        axis['enabled'] = ans != 'n'
        if not axis['enabled']:
            continue
        ans = input('  invert? [y/N] ').strip().lower()
        axis['invert'] = ans == 'y'
        ans = input('  deadzone percent [%d] ' % int(axis['deadzone'] * 100)).strip()
        if ans.isdigit():
            axis['deadzone'] = min(90, int(ans)) / 100.0
    current = int(float(profile.get('ff_gain', 1.0)) * 100)
    print('force feedback strength')
    print('  100 keeps what the game asks for, lower is softer, higher is stronger')
    ans = input('  strength percent [%d] ' % current).strip()
    if ans.isdigit():
        profile['ff_gain'] = max(0, min(200, int(ans))) / 100.0
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
    try:
        return args.func(args)
    except KeyboardInterrupt
        print('\ncancelled, nothing was saved')
        return 130


if __name__ == '__main__':
    sys.exit(main())

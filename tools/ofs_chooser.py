#!/usr/bin/env python3
"""Pick an input device before a game starts. Standard library only."""

import json
import os
import select
import shutil
import subprocess
import sys
import termios
import time
import tty

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.expanduser('~/.config/openforspeed')
CHOICE_FILE = os.path.join(CONFIG_DIR, 'input-choice.json')

sys.path.insert(0, HERE)
import ofs_input as ofs

TERMINALS = [
    ('ghostty', ['-e']), ('gnome-terminal', ['--']), ('konsole', ['-e']),
    ('xfce4-terminal', ['-x']), ('alacritty', ['-e']), ('kitty', []),
    ('foot', []), ('xterm', ['-e']),
]

BOLD = '\033[1m'
DIM = '\033[2m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
CYAN = '\033[36m'
RED = '\033[31m'
RESET = '\033[0m'

COUNTDOWN = 8


def load_choices():
    try:
        with open(CHOICE_FILE) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def save_choice(game, mode):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = load_choices()
    data[game] = mode
    with open(CHOICE_FILE, 'w') as handle:
        json.dump(data, handle, indent=2)


def forget_choice(game):
    data = load_choices()
    if data.pop(game, None) is None:
        return
    with open(CHOICE_FILE, 'w') as handle:
        json.dump(data, handle, indent=2)


def find_terminal():
    for name, flag in TERMINALS:
        path = shutil.which(name)
        if path:
            return [path] + flag
    return None


def detect_devices():
    devices = ofs.list_devices()
    wheel = next((d for d in devices if ofs.looks_like_wheel(d['name'])), None)
    pad = next((d for d in devices if not ofs.looks_like_wheel(d['name'])), None)
    return wheel, pad


def profile_summary(name):
    profile = ofs.load_profile(name)
    if not profile:
        return None
    axes = profile.get('axes', {})
    kept = [a for a in axes.values() if a.get('enabled')]
    dropped = len(axes) - len(kept)
    inverted = sum(1 for a in kept if a.get('invert'))
    parts = ['%d axes' % len(kept)]
    if dropped:
        parts.append('%d dropped' % dropped)
    if inverted:
        parts.append('%d inverted' % inverted)
    return ', '.join(parts)


def off_centre_axes(dev):
    if not dev:
        return []
    out = []
    fd = os.open(dev['path'], os.O_RDONLY | os.O_NONBLOCK)
    for code in dev['axes']:
        info = ofs.read_axis(fd, code)
        if not info or info.maximum == info.minimum:
            continue
        span = info.maximum - info.minimum
        centre = (info.minimum + info.maximum) / 2
        if abs(info.value - centre) / span > 0.4:
            out.append(ofs.AXIS_NAMES.get(code, str(code)))
    os.close(fd)
    return out


def option_line(key, label, dev, profile_name, warnings):
    if not dev and profile_name:
        return '   %s  %-9s %snot connected%s' % (key, label, DIM, RESET)
    name = dev['name'][:30] if dev else ''
    summary = profile_summary(profile_name) if profile_name else None
    if summary:
        status = '%scalibrated%s %s(%s)%s' % (GREEN, RESET, DIM, summary, RESET)
    elif profile_name:
        status = '%snot calibrated yet%s' % (YELLOW, RESET)
    else:
        status = '%sno setup needed%s' % (DIM, RESET)
    line = '   %s  %-9s %-32s %s' % (key, label, name, status)
    if warnings:
        line += '\n        %s%s rests off centre, it will hold menus%s' % (
            YELLOW, ', '.join(warnings), RESET)
    return line


def draw(game, wheel, pad, remembered, seconds_left, message):
    sys.stdout.write('\033[H\033[J')
    print()
    print('  %sOpenForSpeed%s   %s%s%s' % (BOLD, RESET, CYAN, game, RESET))
    print('  ' + '=' * 58)
    print()
    print(option_line('1', 'Wheel', wheel, 'wheel', off_centre_axes(wheel)))
    print(option_line('2', 'Gamepad', pad, 'gamepad', []))
    print(option_line('3', 'Keyboard', None, None, []))
    print()
    print('  %sc%s calibrate    %sd%s delete a profile    %sf%s forget saved choice'
          % (BOLD, RESET, BOLD, RESET, BOLD, RESET))
    print('  %sq%s quit' % (BOLD, RESET))
    print()
    if message:
        print('  %s' % message)
        print()
    if remembered and seconds_left is not None:
        bar = '#' * seconds_left + '.' * (COUNTDOWN - seconds_left)
        print('  starting with %s%s%s in %s%d%ss  [%s]'
              % (BOLD, remembered, RESET, BOLD, seconds_left, RESET, bar))
        print('  %spress any listed key to stop the countdown%s' % (DIM, RESET))
    else:
        print('  %spick an option%s' % (DIM, RESET))
    sys.stdout.flush()


def read_key(timeout=None):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ready, _, _ = select.select([fd], [], [], timeout)
        if not ready:
            return None
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def run_calibration(kind):
    subprocess.call([sys.executable, os.path.join(HERE, 'ofs_input.py'),
                     'calibrate', '--device', kind, '--profile', kind])


def delete_profile(kind):
    path = ofs.profile_path(kind)
    try:
        os.remove(path)
        return '%sdeleted the %s profile%s' % (GREEN, kind, RESET)
    except OSError:
        return '%sno %s profile to delete%s' % (YELLOW, kind, RESET)


def ask_kind(prompt):
    print()
    print('  %s  [1] wheel  [2] gamepad  [any other key to cancel]' % prompt)
    sys.stdout.flush()
    key = read_key(15)
    return {'1': 'wheel', '2': 'gamepad'}.get(key)


def choose(game):
    wheel, pad = detect_devices()
    remembered = load_choices().get(game)
    if remembered == 'wheel' and not wheel:
        remembered = None
    if remembered == 'gamepad' and not pad:
        remembered = None
    message = ''
    seconds = COUNTDOWN if remembered else None

    while True:
        draw(game, wheel, pad, remembered, seconds, message)
        message = ''
        key = read_key(1 if seconds is not None else None)

        if key is None:
            if seconds is None:
                continue
            seconds -= 1
            if seconds <= 0:
                return remembered
            continue

        seconds = None
        if key in ('1', '2', '3'):
            mode = {'1': 'wheel', '2': 'gamepad', '3': 'keyboard'}[key]
            if mode == 'wheel' and not wheel:
                message = '%sno wheel connected%s' % (YELLOW, RESET)
                continue
            if mode == 'gamepad' and not pad:
                message = '%sno gamepad connected%s' % (YELLOW, RESET)
                continue
            if mode != 'keyboard' and not ofs.load_profile(mode):
                print()
                print('  %s has no profile yet, calibrating first' % mode)
                time.sleep(1.2)
                run_calibration(mode)
            save_choice(game, mode)
            return mode
        if key == 'c':
            kind = ask_kind('calibrate which device?')
            if kind:
                run_calibration(kind)
                message = '%s%s profile saved%s' % (GREEN, kind, RESET)
        elif key == 'd':
            kind = ask_kind('delete which profile?')
            if kind:
                message = delete_profile(kind)
        elif key == 'f':
            forget_choice(game)
            remembered = None
            message = '%ssaved choice cleared%s' % (GREEN, RESET)
        elif key in ('q', '\x03'):
            return None


def start_bridge(profile='wheel'):
    if not os.access('/dev/uinput', os.W_OK):
        print('  %s/dev/uinput is not writable, running without the bridge%s'
              % (YELLOW, RESET))
        return None
    proc = subprocess.Popen(
        [sys.executable, os.path.join(HERE, 'ofs_input.py'),
         'bridge', '--profile', profile],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    if proc.poll() is not None:
        print('  %sthe bridge did not start, using the wheel directly%s'
              % (YELLOW, RESET))
        return None
    return proc


def main():
    if len(sys.argv) < 3:
        print('usage: ofs_chooser.py <game-id> <command> [args...]')
        return 2
    game = sys.argv[1]
    command = sys.argv[2:]

    if not sys.stdin.isatty():
        term = find_terminal()
        if term:
            os.execvp(term[0], term + [sys.executable,
                                       os.path.abspath(__file__)] + sys.argv[1:])
        os.execvp(command[0], command)

    mode = choose(game)
    if mode is None:
        return 0

    bridge = None
    if mode == 'wheel':
        setup = os.path.expanduser('~/Games/nfs-wheel-setup.sh')
        if os.access(setup, os.X_OK):
            subprocess.call([setup, '20'])
        bridge = start_bridge()

    print()
    print('  %sstarting %s with %s%s' % (GREEN, game, mode, RESET))
    print()
    try:
        subprocess.call(command)
    finally:
        if bridge:
            bridge.terminate()
    return 0


if __name__ == '__main__':
    sys.exit(main())

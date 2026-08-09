#!/usr/bin/env python3
"""Pick an input device before a game starts. Standard library only."""

import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.expanduser('~/.config/openforspeed')
CHOICE_FILE = os.path.join(CONFIG_DIR, 'input-choice.json')

sys.path.insert(0, HERE)
import ofs_input as ofs

TERMINALS = [
    ('ghostty', ['-e']),
    ('gnome-terminal', ['--']),
    ('konsole', ['-e']),
    ('xfce4-terminal', ['-x']),
    ('alacritty', ['-e']),
    ('kitty', []),
    ('xterm', ['-e']),
]

BOLD, DIM, GREEN, YELLOW, RESET = (
    '\033[1m', '\033[2m', '\033[32m', '\033[33m', '\033[0m')


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
    data.pop(game, None)
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


def axis_warnings(dev):
    if not dev:
        return []
    warnings = []
    fd = os.open(dev['path'], os.O_RDONLY | os.O_NONBLOCK)
    for code in dev['axes']:
        info = ofs.read_axis(fd, code)
        if not info or info.maximum == info.minimum:
            continue
        span = info.maximum - info.minimum
        centre = (info.minimum + info.maximum) / 2
        if abs(info.value - centre) / span > 0.4:
            warnings.append(ofs.AXIS_NAMES.get(code, str(code)))
    os.close(fd)
    return warnings


def draw_menu(game, wheel, pad, remembered):
    os.system('clear')
    print()
    print('  %sOpenForSpeed%s  %s%s%s' % (BOLD, RESET, DIM, game, RESET))
    print('  ' + '-' * 46)
    print()
    if wheel:
        warn = axis_warnings(wheel)
        note = ''
        if warn:
            note = '  %s%d axis rests off centre%s' % (YELLOW, len(warn), RESET)
        print('   1  Wheel    %s%s' % (wheel['name'][:34], note))
    else:
        print('   1  Wheel    %snot connected%s' % (DIM, RESET))
    if pad:
        print('   2  Gamepad  %s' % pad['name'][:34])
    else:
        print('   2  Gamepad  %snot connected%s' % (DIM, RESET))
    print('   3  Keyboard %sno device setup%s' % (DIM, RESET))
    print()
    print('   c  Calibrate the wheel first')
    print('   f  Forget the saved choice for this game')
    print()
    if remembered:
        print('  %ssaved choice: %s, starting in 5s%s' % (DIM, remembered, RESET))
        print('  %spress a number to change it%s' % (DIM, RESET))
    print()


def read_key(timeout=None):
    import select
    import termios
    import tty
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


def choose(game):
    wheel, pad = detect_devices()
    choices = load_choices()
    remembered = choices.get(game)
    while True:
        draw_menu(game, wheel, pad, remembered)
        key = read_key(5 if remembered else None)
        if key is None and remembered:
            return remembered
        if key in ('1', '2', '3'):
            mode = {'1': 'wheel', '2': 'gamepad', '3': 'keyboard'}[key]
            if mode == 'wheel' and not wheel:
                continue
            if mode == 'gamepad' and not pad:
                continue
            save_choice(game, mode)
            return mode
        if key == 'c':
            if wheel:
                subprocess.call([sys.executable,
                                 os.path.join(HERE, 'ofs_input.py'),
                                 'calibrate', '--profile', 'wheel'])
            remembered = None
        if key == 'f':
            forget_choice(game)
            remembered = None
        if key in ('q', '\x03'):
            return None


def start_bridge(profile='wheel'):
    if not os.access('/dev/uinput', os.W_OK):
        print('  %s/dev/uinput not writable, skipping the bridge%s' % (YELLOW, RESET))
        return None
    if not ofs.load_profile(profile):
        dev = ofs.pick_device('wheel')
        if dev:
            ofs.save_profile(profile, ofs.default_profile(dev))
    proc = subprocess.Popen(
        [sys.executable, os.path.join(HERE, 'ofs_input.py'),
         'bridge', '--profile', profile],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    if proc.poll() is not None:
        return None
    return proc


def main():
    if len(sys.argv) < 3:
        print('usage: ofs_chooser.py <game-id> <launcher> [args...]')
        return 2
    game = sys.argv[1]
    command = sys.argv[2:]

    if not sys.stdin.isatty():
        term = find_terminal()
        if term:
            os.execvp(term[0], term + [sys.executable, os.path.abspath(__file__)] + sys.argv[1:])
        os.execvp(command[0], command)

    mode = choose(game)
    if mode is None:
        return 0

    bridge = None
    if mode == 'wheel':
        wheel_setup = os.path.expanduser('~/Games/nfs-wheel-setup.sh')
        if os.access(wheel_setup, os.X_OK):
            subprocess.call([wheel_setup, '20'])
        bridge = start_bridge()

    print()
    print('  %sstarting with %s%s' % (GREEN, mode, RESET))
    print()
    try:
        subprocess.call(command)
    finally:
        if bridge:
            bridge.terminate()
    return 0


if __name__ == '__main__':
    sys.exit(main())

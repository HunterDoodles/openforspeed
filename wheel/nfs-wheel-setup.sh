#!/usr/bin/env bash
set -uo pipefail

DEADZONE_PERCENT="${1:-20}"

find_modes_file() { find /sys -name "alternate_modes" 2>/dev/null | head -1; }

MODES=$(find_modes_file)
if [[ -n "$MODES" ]] && ! grep -qE '^native:.*\*' "$MODES"; then
    if command -v flatpak >/dev/null 2>&1 && flatpak info io.github.berarma.Oversteer >/dev/null 2>&1; then
        flatpak run io.github.berarma.Oversteer --mode G29 >/dev/null 2>&1 || true
        for _ in $(seq 1 20); do
            sleep 1
            ls /dev/input/by-id/*Logitech*event-joystick >/dev/null 2>&1 && break
        done
        sleep 2
    fi
fi

MODES=$(find_modes_file)
if [[ -n "$MODES" ]]; then
    D=$(dirname "$MODES")
    [[ -w "$D/combine_pedals" ]] && echo 1 > "$D/combine_pedals" 2>/dev/null
fi

python3 - "$DEADZONE_PERCENT" <<'PY' 2>/dev/null || true
import glob, os, sys, ctypes, fcntl

class AbsInfo(ctypes.Structure):
    _fields_ = [('value', ctypes.c_int32), ('minimum', ctypes.c_int32),
                ('maximum', ctypes.c_int32), ('fuzz', ctypes.c_int32),
                ('flat', ctypes.c_int32), ('resolution', ctypes.c_int32)]

CLUTCH_AXIS = 1
PEDAL_AXES = (2, 5)
percent = int(sys.argv[1]) / 100.0

for path in glob.glob('/dev/input/by-id/*event-joystick'):
    name = os.path.basename(path).lower()
    if not any(k in name for k in ('wheel', 'racing', 'logitech')):
        continue
    try:
        fd = os.open(os.path.realpath(path), os.O_RDWR)
    except OSError:
        continue
    for code in (CLUTCH_AXIS,) + PEDAL_AXES:
        info = AbsInfo()
        try:
            fcntl.ioctl(fd, 0x80184540 + code, info)
        except OSError:
            continue
        span = info.maximum - info.minimum
        if span == 0:
            continue
        if code == CLUTCH_AXIS:
            info.flat = span
        else:
            info.flat = int(span * percent)
        try:
            fcntl.ioctl(fd, 0x401845c0 + code, info)
        except OSError:
            pass
    os.close(fd)
PY

#!/usr/bin/env bash
set -euo pipefail

readonly SCRIPT_NAME="OpenForSpeed"
readonly GE_PROTON_VERSION="GE-Proton11-3"
readonly GE_PROTON_URL="https://github.com/GloriousEggroll/proton-ge-custom/releases/download/${GE_PROTON_VERSION}/${GE_PROTON_VERSION}.tar.gz"

readonly GAMES_ROOT="$HOME/Games"
readonly RUNNERS_DIR="$GAMES_ROOT/_runners"
readonly STAGING_DIR="$GAMES_ROOT/_installers/nfs"
readonly MODS_DIR="$GAMES_ROOT/_installers/nfs/mods"
readonly XI_VERSION="1.22"
readonly XI_BASE="https://github.com/xan1242/NFS-XtendedInput/releases/download/${XI_VERSION}"
readonly WSFP_TAGS="https://api.github.com/repos/ThirteenAG/WidescreenFixesPack/releases/tags"
readonly ICON_DIR="$HOME/.local/share/icons"
readonly APPS_DIR="$HOME/.local/share/applications"

readonly GAME_IDS=(underground underground-2 most-wanted carbon prostreet undercover nfs3 hot-pursuit-2)

SOURCE_DIR=""
STEAM_ROOT=""
PROTON_BIN=""
CHECK_ONLY=0
TUNE_ONLY=0
NO_TUNE=0
INPUT_MODE="gamepad"
SELECTED=()

HW_RES_X=1920
HW_RES_Y=1080
HW_GPU_VENDOR="0x10DE"
HW_GPU_NAME="unknown"
HW_VRAM_MB=0
HW_THREADS=1
HW_PAD=0
HW_TIER="medium"

GAME_LABEL=""
GAME_ZIP_GLOB=""
GAME_DIRNAME=""
GAME_OVERRIDES=""
GAME_KIND=""
GAME_SIZE_GB=0

C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'; C_GREEN=$'\033[32m'
C_YELLOW=$'\033[33m'; C_RED=$'\033[31m'; C_BLUE=$'\033[34m'

log()  { printf '%s\n' "$*"; }
info() { printf '%s==>%s %s\n' "$C_BLUE$C_BOLD" "$C_RESET" "$*"; }
ok()   { printf '  %s[ ok ]%s %s\n' "$C_GREEN" "$C_RESET" "$*"; }
warn() { printf '  %s[warn]%s %s\n' "$C_YELLOW" "$C_RESET" "$*"; }
fail() { printf '  %s[fail]%s %s\n' "$C_RED" "$C_RESET" "$*"; }
die()  { printf '\n%sError:%s %s\n' "$C_RED$C_BOLD" "$C_RESET" "$*" >&2; exit 1; }

load_game() {
    GAME_KIND="magipack"
    GAME_OVERRIDES="dinput8=n,b"
    case "$1" in
        underground)
            GAME_LABEL="Need for Speed Underground"
            GAME_ZIP_GLOB="Need-for-Speed-Underground_*.zip"
            GAME_DIRNAME="NFSU"; GAME_SIZE_GB=3 ;;
        underground-2)
            GAME_LABEL="Need for Speed Underground 2"
            GAME_ZIP_GLOB="Need-for-Speed-Underground-2_*.zip"
            GAME_DIRNAME="NFSU2"; GAME_SIZE_GB=5 ;;
        most-wanted)
            GAME_LABEL="Need for Speed Most Wanted"
            GAME_ZIP_GLOB="Need-for-Speed-Most-Wanted_*.zip"
            GAME_DIRNAME="NFSMW"; GAME_SIZE_GB=5
            GAME_OVERRIDES="dinput8=n,b;dsound=n,b" ;;
        carbon)
            GAME_LABEL="Need for Speed Carbon"
            GAME_ZIP_GLOB="Need-for-Speed-Carbon_*.zip"
            GAME_DIRNAME="NFSC"; GAME_SIZE_GB=7 ;;
        prostreet)
            GAME_LABEL="Need for Speed ProStreet"
            GAME_ZIP_GLOB="Need-for-Speed-ProStreet_*.zip"
            GAME_DIRNAME="NFSPS"; GAME_SIZE_GB=10; GAME_KIND="isorepack" ;;
        undercover)
            GAME_LABEL="Need for Speed Undercover"
            GAME_ZIP_GLOB="Need-for-Speed-Undercover_*.zip"
            GAME_DIRNAME="NFSUC"; GAME_SIZE_GB=12 ;;
        hot-pursuit-2)
            GAME_LABEL="Need for Speed Hot Pursuit 2"
            GAME_ZIP_GLOB="Need-for-Speed-Hot-Pursuit-2_*.zip"
            GAME_DIRNAME="Need For Speed - Hot Pursuit 2"; GAME_SIZE_GB=3
            GAME_KIND="advinst"; GAME_OVERRIDES="d3d8=b;dinput8=n,b" ;;
        nfs3)
            GAME_LABEL="Need for Speed III Hot Pursuit"
            GAME_ZIP_GLOB="Need-for-Speed-III-Hot-Pursuit_*.zip"
            GAME_DIRNAME="NFS3"; GAME_SIZE_GB=2
            GAME_KIND="bundle7z"; GAME_OVERRIDES="" ;;
        *)  return 1 ;;
    esac
}

usage() {
    cat <<EOF
$SCRIPT_NAME

Usage:
  ./install.sh --source <folder> --game <id>
  ./install.sh --source <folder> --all
  ./install.sh --list
  ./install.sh --check --source <folder>

Options:
  --source <folder>  Folder with the game zips. Searched recursively.
  --game <id>        Install one game. Repeat the flag for several.
  --all              Install every game found in the source folder.
  --list             Show the supported game ids and exit.
  --check            Run the system checks and exit.
  --tune-only        Only rewrite the graphics config of installed games.
  --no-tune          Install without touching the graphics config.
  --input <mode>     gamepad (default) or wheel. XtendedInput gives the best
                     gamepad handling but disables DirectInput, which is how
                     racing wheels are seen. Pick wheel to keep them working.
  --help             Show this message.

Example:
  ./install.sh --source /media/user/USB/Download --game most-wanted
EOF
}

list_games() {
    printf '%s\n\n' "Supported games:"
    local id
    for id in "${GAME_IDS[@]}"; do
        load_game "$id"
        printf '  %-16s %-38s ~%s GB\n' "$id" "$GAME_LABEL" "$GAME_SIZE_GB"
    done
    printf '\n%s\n' "Hot Pursuit 2 needs one manual step after install, see the README."
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --source) SOURCE_DIR="${2:-}"; shift 2 ;;
            --game)   SELECTED+=("${2:-}"); shift 2 ;;
            --all)    SELECTED=("${GAME_IDS[@]}"); shift ;;
            --list)   list_games; exit 0 ;;
            --check)  CHECK_ONLY=1; shift ;;
            --tune-only) TUNE_ONLY=1; shift ;;
            --no-tune)   NO_TUNE=1; shift ;;
            --input)     INPUT_MODE="${2:-gamepad}"; shift 2 ;;
            --help|-h) usage; exit 0 ;;
            *) die "Unknown option: $1 (try --help)" ;;
        esac
    done
}

detect_distro() {
    if [[ -r /etc/os-release ]]; then . /etc/os-release; printf '%s' "${PRETTY_NAME:-unknown}"
    else printf '%s' "unknown"; fi
}

check_not_root() {
    [[ $EUID -ne 0 ]] || die "Do not run this as root. Everything goes into your home folder."
    ok "running as $USER, no root needed"
}

check_tools() {
    local missing=() tool
    for tool in curl tar unzip python3 find; do
        command -v "$tool" >/dev/null 2>&1 || missing+=("$tool")
    done
    command -v 7z >/dev/null 2>&1 || command -v 7za >/dev/null 2>&1 || missing+=("p7zip")
    if [[ ${#missing[@]} -gt 0 ]]; then fail "missing tools: ${missing[*]}"; return 1; fi
    ok "curl, tar, unzip, 7z and python3 are available"
}

required_space_gb() {
    local total=0 id
    for id in "${SELECTED[@]}"; do load_game "$id" && total=$((total + GAME_SIZE_GB)); done
    printf '%s' "$((total + 10))"
}

check_disk_space() {
    local avail need
    avail=$(df -BG --output=avail "$HOME" | tail -1 | tr -dc '0-9')
    need=$(required_space_gb)
    if [[ -z "$avail" ]] || [[ "$avail" -lt "$need" ]]; then
        fail "${avail:-0} GB free in \$HOME, the selection needs about ${need} GB"
        return 1
    fi
    ok "${avail} GB free, selection needs about ${need} GB"
}

check_gpu() {
    local gpu
    gpu=$(lspci 2>/dev/null | grep -iE 'vga|3d|display' | head -1 | sed 's/.*: //') || true
    [[ -n "$gpu" ]] && ok "GPU: $gpu" || warn "could not read the GPU model"
}

check_vulkan() {
    if command -v vulkaninfo >/dev/null 2>&1; then
        local driver
        driver=$(vulkaninfo --summary 2>/dev/null | grep -m1 'driverInfo' | sed 's/.*= *//') || true
        [[ -n "$driver" ]] && { ok "Vulkan driver: $driver"; return 0; }
    fi
    local icd
    icd=$(find /usr/share/vulkan/icd.d /etc/vulkan/icd.d -name '*.json' 2>/dev/null | wc -l)
    [[ "$icd" -gt 0 ]] && { ok "Vulkan ICD files found ($icd)"; return 0; }
    fail "no Vulkan driver detected, DXVK will not run"
    return 1
}

find_steam_root() {
    local c
    for c in "$HOME/.steam/root" "$HOME/.steam/debian-installation" \
             "$HOME/.local/share/Steam" \
             "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam"; do
        [[ -d "$c" ]] && { printf '%s' "$c"; return 0; }
    done
    return 1
}

check_steam() {
    if STEAM_ROOT=$(find_steam_root); then ok "Steam data found at $STEAM_ROOT"
    else STEAM_ROOT="$HOME/.steam/root"; warn "Steam not found, using $STEAM_ROOT for the runner"; fi
}

check_proton() {
    local dir="$STEAM_ROOT/compatibilitytools.d/$GE_PROTON_VERSION"
    if [[ -x "$dir/proton" ]]; then PROTON_BIN="$dir/proton"; ok "$GE_PROTON_VERSION already installed"
    else warn "$GE_PROTON_VERSION will be downloaded"; fi
}

detect_resolution() {
    local geom=""
    if command -v xrandr >/dev/null 2>&1; then
        geom=$(xrandr 2>/dev/null | grep -E " connected primary [0-9]+x[0-9]+" \
               | grep -oE "[0-9]+x[0-9]+" | head -1)
        [[ -n "$geom" ]] || geom=$(xrandr 2>/dev/null | grep -E " connected [0-9]+x[0-9]+" \
               | grep -oE "[0-9]+x[0-9]+" | head -1)
    fi
    if [[ -z "$geom" ]] && command -v wlr-randr >/dev/null 2>&1; then
        geom=$(wlr-randr 2>/dev/null | grep -oE "[0-9]+x[0-9]+" | head -1)
    fi
    [[ -n "$geom" ]] || return 1
    HW_RES_X="${geom%x*}"
    HW_RES_Y="${geom#*x}"
}

detect_gpu() {
    local id
    id=$(lspci -nn 2>/dev/null | grep -iE "vga|3d|display" | grep -oE "\[[0-9a-f]{4}:[0-9a-f]{4}\]" | head -1)
    HW_GPU_NAME=$(lspci 2>/dev/null | grep -iE "vga|3d|display" | head -1 | sed 's/.*: //')
    case "$id" in
        \[10de:*) HW_GPU_VENDOR="0x10DE" ;;
        \[1002:*) HW_GPU_VENDOR="0x1002" ;;
        \[8086:*) HW_GPU_VENDOR="0x8086" ;;
    esac
}

detect_vram() {
    local mb=0
    if command -v nvidia-smi >/dev/null 2>&1; then
        mb=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1)
    fi
    if [[ -z "$mb" || "$mb" -eq 0 ]] 2>/dev/null; then
        local bytes
        bytes=$(cat /sys/class/drm/card*/device/mem_info_vram_total 2>/dev/null | sort -rn | head -1)
        [[ -n "$bytes" ]] && mb=$((bytes / 1024 / 1024))
    fi
    if [[ -z "$mb" || "$mb" -eq 0 ]] 2>/dev/null; then
        mb=$(vulkaninfo --summary 2>/dev/null | grep -oE "size = [0-9]+" | head -1 | grep -oE "[0-9]+")
        [[ -n "$mb" ]] && mb=$((mb / 1024 / 1024))
    fi
    HW_VRAM_MB=${mb:-0}
}

detect_hardware() {
    detect_resolution || true
    detect_gpu
    detect_vram
    HW_THREADS=$(nproc 2>/dev/null || printf '1')
    HW_PAD=$(ls /dev/input/js* 2>/dev/null | wc -l)
    if   [[ "$HW_VRAM_MB" -ge 6000 ]]; then HW_TIER="high"
    elif [[ "$HW_VRAM_MB" -ge 2000 ]]; then HW_TIER="medium"
    elif [[ "$HW_VRAM_MB" -gt 0    ]]; then HW_TIER="low"
    else HW_TIER="medium"; fi
}

report_hardware() {
    ok "display: ${HW_RES_X}x${HW_RES_Y}"
    ok "GPU: $HW_GPU_NAME (vendor $HW_GPU_VENDOR)"
    if [[ "$HW_VRAM_MB" -gt 0 ]]; then ok "VRAM: ${HW_VRAM_MB} MB, quality preset: $HW_TIER"
    else warn "could not read VRAM, using the $HW_TIER preset"; fi
    [[ "$HW_PAD" -gt 0 ]] && ok "gamepad detected, controller icons will be enabled" \
                          || warn "no gamepad detected, keyboard icons will be kept"
}

ini_set() {
    local file="$1" key="$2" value="$3"
    [[ -f "$file" ]] || return 0
    grep -qE "^[[:space:]]*${key}[[:space:]]*=" "$file" || return 0
    awk -v k="$key" -v v="$value" '
        BEGIN { done = 0 }
        {
            if (!done && match($0, "^[ \t]*" k "[ \t]*=")) {
                head = substr($0, 1, RLENGTH)
                rest = substr($0, RLENGTH + 1)
                ci = index(rest, ";")
                if (ci > 0) printf "%s %-30s %s\n", head, v, substr(rest, ci)
                else        printf "%s %s\n", head, v
                done = 1
                next
            }
            print
        }
    ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
}

tune_widescreen() {
    local f="$1"
    ini_set "$f" "ResX" "$HW_RES_X"
    ini_set "$f" "ResY" "$HW_RES_Y"
    ini_set "$f" "FixHUD" "1"
    ini_set "$f" "FixFOV" "1"
    ini_set "$f" "AutoFitFE" "1"
    ini_set "$f" "AutoFitFMV" "1"
    ini_set "$f" "SkipIntro" "1"
    ini_set "$f" "ForceHighSpecAudio" "1"
    ini_set "$f" "ForcedGPUVendor" "$HW_GPU_VENDOR"
    ini_set "$f" "ResDetect" "1"
    ini_set "$f" "FixAspectRatio" "1"
    ini_set "$f" "FramerateUncap" "1"
    ini_set "$f" "PostRaceFix" "1"
    ini_set "$f" "BrakeLightFix" "1"
    ini_set "$f" "GammaFix" "1"
    ini_set "$f" "DamageMemoryLeakFix" "1"
    ini_set "$f" "AntiTrackStreamerCrash" "1"
    ini_set "$f" "AntiFEScriptCrash" "1"
    ini_set "$f" "DisablePunkBuster" "1"
    [[ "$HW_PAD" -gt 0 ]] && ini_set "$f" "ImproveGamepadSupport" "1"
    local wm
    wm=$(grep -E "^[[:space:]]*WindowedMode[[:space:]]*=" "$f" 2>/dev/null | head -1 \
         | sed -E 's/^[^=]*=[[:space:]]*//' | grep -oE "^[0-9]+")
    if [[ -n "$wm" ]] && [[ "$wm" -ge 1 ]] && [[ "$wm" -le 3 ]]; then
        ini_set "$f" "WindowedMode" "4"
    fi
    case "$HW_TIER" in
        high)
            ini_set "$f" "ShadowsRes" "8192"
            ini_set "$f" "ShadowRes" "8192"
            ini_set "$f" "ImproveShadowLOD" "1"
            ini_set "$f" "AutoScaleShadowsRes" "1"
            ini_set "$f" "ShadowsFix" "1"
            ini_set "$f" "ImproveSceneryLOD" "1"
            ini_set "$f" "HudAspectRatioConstraint" "Auto" ;;
        medium)
            ini_set "$f" "ShadowsRes" "4096"
            ini_set "$f" "ShadowRes" "4096"
            ini_set "$f" "ImproveShadowLOD" "1"
            ini_set "$f" "AutoScaleShadowsRes" "1"
            ini_set "$f" "ShadowsFix" "1" ;;
        low)
            ini_set "$f" "ShadowsRes" "1024"
            ini_set "$f" "ShadowRes" "2048"
            ini_set "$f" "ImproveShadowLOD" "0"
            ini_set "$f" "AutoScaleShadowsRes" "0" ;;
    esac
}

tune_reflections() {
    local f="$1"
    ini_set "$f" "HDReflections" "1"
    ini_set "$f" "ImproveReflectionLOD" "1"
    ini_set "$f" "ForceEnableMirror" "1"
    case "$HW_TIER" in
        high)
            ini_set "$f" "VehicleScale" "2.0"
            ini_set "$f" "RoadScale" "2.0"
            ini_set "$f" "MirrorScale" "2.0"
            ini_set "$f" "Scale" "2.0"
            ini_set "$f" "RestoreShaders" "1"
            ini_set "$f" "RestoreShadows" "1"
            ini_set "$f" "RestoreDetails" "2"
            ini_set "$f" "ImproveReflectionSkybox" "1"
            ini_set "$f" "ExtendRenderDistance" "1"
            ini_set "$f" "RealFrontEndReflections" "1"
            ini_set "$f" "MissingReflectionFix" "1" ;;
        medium)
            ini_set "$f" "VehicleScale" "1.5"
            ini_set "$f" "RoadScale" "1.5"
            ini_set "$f" "MirrorScale" "1.5"
            ini_set "$f" "Scale" "1.5"
            ini_set "$f" "ImproveReflectionSkybox" "1"
            ini_set "$f" "MissingReflectionFix" "1"
            ini_set "$f" "RestoreShadows" "0" ;;
        low)
            ini_set "$f" "VehicleScale" "1.0"
            ini_set "$f" "RoadScale" "1.0"
            ini_set "$f" "MirrorScale" "1.0"
            ini_set "$f" "Scale" "1.0"
            ini_set "$f" "OldGPUCompatibility" "1"
            ini_set "$f" "RestoreShadows" "0" ;;
    esac
}

xtendedinput_pack() {
    case "$1" in
        most-wanted) printf 'MW' ;;
        carbon)      printf 'Carbon' ;;
        prostreet)   printf 'ProStreet' ;;
        undercover)  printf 'UC' ;;
        *) return 1 ;;
    esac
}

set_xtendedinput_state() {
    local dir="$1" want="$2" asi="$dir/scripts/NFS_XtendedInput.asi"
    if [[ "$want" == "off" ]]; then
        [[ -f "$asi" ]] && { mv "$asi" "$asi.off"; ok "XtendedInput disabled so the wheel keeps working"; }
    else
        [[ -f "$asi.off" ]] && { mv "$asi.off" "$asi"; ok "XtendedInput enabled"; }
    fi
    return 0
}

install_xtendedinput() {
    local id="$1" dir="$2" pack zip
    pack=$(xtendedinput_pack "$id") || return 0
    if [[ "$INPUT_MODE" == "wheel" ]]; then
        set_xtendedinput_state "$dir" off
        return 0
    fi
    set_xtendedinput_state "$dir" on
    [[ -f "$dir/scripts/NFS_XtendedInput.asi" ]] && return 0
    [[ -f "$dir/dinput8.dll" ]] || return 0
    mkdir -p "$MODS_DIR"
    zip="$MODS_DIR/xtendedinput-$pack.zip"
    if [[ ! -f "$zip" ]]; then
        curl -sL --fail -o "$zip" "$XI_BASE/Release-$pack-Pack.zip" 2>/dev/null || { warn "could not fetch XtendedInput for $GAME_LABEL"; return 0; }
    fi
    unzip -o -q "$zip" -x "dinput8.dll" -d "$dir" 2>/dev/null
    ok "XtendedInput added, gamepad handling now matches the other games"
}

install_prostreet_fix() {
    local dir="$1" url zip="$MODS_DIR/nfsps-fusionfix.zip"
    [[ -f "$dir/scripts/NFSProStreet.FusionFix.asi" ]] && return 0
    mkdir -p "$MODS_DIR"
    if [[ ! -f "$zip" ]]; then
        url=$(curl -sL "$WSFP_TAGS/nfsps" 2>/dev/null | grep -oE '"browser_download_url": "[^"]*\.zip"' | head -1 | cut -d'"' -f4)
        [[ -n "$url" ]] || { warn "could not fetch the ProStreet widescreen fix"; return 0; }
        curl -sL --fail -o "$zip" "$url" 2>/dev/null || return 0
    fi
    unzip -o -q "$zip" -d "$dir" 2>/dev/null
    ok "widescreen fix added"
}

tune_xtendedinput() {
    local f="$1"
    ini_set "$f" "PassConnStatus" "1"
    ini_set "$f" "XInputOmniMode" "0"
    ini_set "$f" "PercentLS" "0.24"
    ini_set "$f" "PercentRS" "0.24"
    ini_set "$f" "PercentLS_P2" "0.24"
    ini_set "$f" "PercentRS_P2" "0.24"
    ini_set "$f" "Percent_Shifting" "0.75"
    ini_set "$f" "Percent_AnalogStickDigital" "0.50"
}

tune_nfs3() {
    local f="$1"
    ini_set "$f" "ThrashDriver" "nglide"
    ini_set "$f" "NoMovies" "1"
    ini_set "$f" "IntroSplashTime" "0"
    ini_set "$f" "LoadingSplashTime" "0"
    ini_set "$f" "SingleProcAffinity" "0"
    ini_set "$f" "ScreenshoterEnabled" "1"
    case "$HW_TIER" in
        high)   ini_set "$f" "AllowHugeTextures" "1"; ini_set "$f" "OwnHeapLimitMb" "256" ;;
        medium) ini_set "$f" "AllowHugeTextures" "1"; ini_set "$f" "OwnHeapLimitMb" "128" ;;
        low)    ini_set "$f" "AllowHugeTextures" "0"; ini_set "$f" "OwnHeapLimitMb" "32" ;;
    esac
}

tune_game() {
    local dir="$1"
    [[ "$NO_TUNE" -eq 1 ]] && return 0
    local f count=0
    while IFS= read -r f; do
        case "$(basename "$f")" in
            *WidescreenFix.ini|*GenericFix.ini|*FusionFix.ini)  tune_widescreen "$f"; count=$((count+1)) ;;
            *HDReflections.ini)  tune_reflections "$f"; count=$((count+1)) ;;
            nfs3.ini)            tune_nfs3 "$f"; count=$((count+1)) ;;
            NFS_XtendedInput.ini) tune_xtendedinput "$f"; count=$((count+1)) ;;
        esac
    done < <(find "$dir" -maxdepth 2 -iname "*.ini" 2>/dev/null)
    [[ "$count" -gt 0 ]] && ok "tuned $count config file(s) for ${HW_RES_X}x${HW_RES_Y}, preset $HW_TIER" \
                         || warn "no ThirteenAG config files found, nothing to tune"
}

find_zip() {
    find "$SOURCE_DIR" -maxdepth 4 -iname "$1" 2>/dev/null | head -1
}

check_sources() {
    [[ -n "$SOURCE_DIR" ]] || die "Missing --source <folder>"
    [[ -d "$SOURCE_DIR" ]] || die "Source folder not found: $SOURCE_DIR"
    local id zip found=0
    for id in "${SELECTED[@]}"; do
        load_game "$id" || { fail "unknown game id: $id"; return 1; }
        zip=$(find_zip "$GAME_ZIP_GLOB")
        if [[ -n "$zip" ]]; then ok "$GAME_LABEL: $(basename "$zip")"; found=$((found+1))
        else warn "$GAME_LABEL: no zip matching $GAME_ZIP_GLOB"; fi
    done
    [[ "$found" -gt 0 ]] || { fail "no game archives found in $SOURCE_DIR"; return 1; }
}

discovery() {
    info "Checking your system"
    log "  distro : $(detect_distro)"
    log "  kernel : $(uname -r)"
    log "  session: ${XDG_SESSION_TYPE:-unknown}"
    log ""
    local failed=0
    check_not_root
    check_tools || failed=1
    check_gpu
    check_vulkan || failed=1
    check_steam
    check_proton
    detect_hardware
    report_hardware
    if [[ "$TUNE_ONLY" -eq 0 ]]; then
        check_disk_space || failed=1
        check_sources || failed=1
    fi
    log ""
    [[ "$failed" -eq 0 ]] || die "Fix the items marked [fail] and run again."
    ok "discovery passed"
}

install_proton() {
    [[ -n "$PROTON_BIN" ]] && return 0
    info "Installing $GE_PROTON_VERSION"
    local target="$STEAM_ROOT/compatibilitytools.d"
    mkdir -p "$target" "$RUNNERS_DIR"
    local archive="$RUNNERS_DIR/${GE_PROTON_VERSION}.tar.gz"
    [[ -f "$archive" ]] || curl -L --progress-bar -o "$archive" "$GE_PROTON_URL"
    tar -xf "$archive" -C "$target"
    PROTON_BIN="$target/$GE_PROTON_VERSION/proton"
    [[ -x "$PROTON_BIN" ]] || die "Proton did not unpack correctly"
    ok "$GE_PROTON_VERSION ready"
}

prefix_path() { printf '%s' "$GAMES_ROOT/nfs-$1"; }
game_path()   { printf '%s' "$(prefix_path "$1")/pfx/drive_c/Games/$GAME_DIRNAME"; }

proton_env() {
    export STEAM_COMPAT_CLIENT_INSTALL_PATH="$STEAM_ROOT"
    export STEAM_COMPAT_DATA_PATH="$1"
    export WINEDLLOVERRIDES="lsteamclient=d"
}

create_prefix() {
    local pfx="$1"
    mkdir -p "$pfx"
    proton_env "$pfx"
    python3 "$PROTON_BIN" run cmd /c echo ready >/dev/null 2>&1 || true
    [[ -d "$pfx/pfx/drive_c" ]] || die "Prefix was not created at $pfx"
    mkdir -p "$pfx/pfx/drive_c/Games"
}

unpack_zip() {
    local zip="$1" dest="$2"
    mkdir -p "$dest"
    [[ -n "$(ls -A "$dest" 2>/dev/null)" ]] && return 0
    unzip -o -q "$zip" -d "$dest"
}

install_magipack() {
    local id="$1" zip="$2" pfx="$3"
    local stage="$STAGING_DIR/$id"
    info "Unpacking $GAME_LABEL"
    unpack_zip "$zip" "$stage"
    local setup
    setup=$(find "$stage" -maxdepth 2 -iname "*Setup.exe" | head -1)
    [[ -n "$setup" ]] || die "No Setup.exe inside $zip"
    info "Installing $GAME_LABEL, this takes a few minutes"
    proton_env "$pfx"
    ( cd "$(dirname "$setup")" && python3 "$PROTON_BIN" run "$setup" \
        /VERYSILENT /SUPPRESSMSGBOXES /NORESTART "/DIR=C:\\Games\\$GAME_DIRNAME" ) >/dev/null 2>&1 || true
}

install_isorepack() {
    local id="$1" zip="$2" pfx="$3"
    local stage="$STAGING_DIR/$id"
    info "Unpacking $GAME_LABEL"
    unpack_zip "$zip" "$stage"
    local iso
    iso=$(find "$stage" -maxdepth 2 -iname "*.iso" | head -1)
    [[ -n "$iso" ]] || die "No iso inside $zip"
    if [[ ! -f "$stage/iso/setup.exe" ]]; then
        info "Extracting the disc image"
        7z x -y -o"$stage/iso" "$iso" >/dev/null 2>&1
    fi
    [[ -f "$stage/iso/setup.exe" ]] || die "No setup.exe inside the disc image"
    info "Installing $GAME_LABEL, this takes a few minutes"
    proton_env "$pfx"
    ( cd "$stage/iso" && python3 "$PROTON_BIN" run "$stage/iso/setup.exe" \
        /VERYSILENT /SUPPRESSMSGBOXES /NORESTART "/DIR=C:\\Games\\$GAME_DIRNAME" ) >/dev/null 2>&1 || true
}

install_bundle7z() {
    local id="$1" zip="$2" pfx="$3"
    local stage="$STAGING_DIR/$id"
    info "Unpacking $GAME_LABEL"
    unpack_zip "$zip" "$stage"
    local base
    base=$(find "$stage" -iname "*base_eng.7z" | head -1)
    [[ -n "$base" ]] || die "No base archive inside $zip"
    local dest="$pfx/pfx/drive_c/Games/$GAME_DIRNAME"
    mkdir -p "$dest"
    info "Extracting $GAME_LABEL"
    7z x -y -o"$dest" "$base" >/dev/null 2>&1
}

detect_exe() {
    local dir="$1"
    find "$dir" -maxdepth 1 -iname "*.exe" ! -iname "unins*" -printf '%s %f\n' 2>/dev/null \
        | sort -rn | head -1 | cut -d' ' -f2-
}

write_launcher() {
    local id="$1" pfx="$2" dir="$3" exe="$4" overrides="$5" label="$6"
    local path="$GAMES_ROOT/nfs-$id-play.sh"
    cat > "$path" <<EOF
#!/usr/bin/env bash
set -uo pipefail

PROTON="$PROTON_BIN"
GAME_DIR="$dir"
TARGET="\$GAME_DIR/$exe"

[[ -e "\$PROTON" ]] || { echo "Proton not found at \$PROTON" >&2; exit 1; }
[[ -e "\$TARGET" ]] || { echo "Not found: \$TARGET" >&2; exit 1; }

if pgrep -x steam >/dev/null 2>&1 && command -v zenity >/dev/null 2>&1; then
    zenity --question --no-wrap --title="$label" \\
        --text="Steam is running.\\n\\nSteam Input grabs the controller and the game stops\\nreacting to it. Closing Steam is the easy fix.\\n\\nStart anyway?" \\
        --ok-label="Start anyway" --cancel-label="Cancel" 2>/dev/null || exit 0
fi

WHEEL_PROFILE="nfs-$id"
if command -v flatpak >/dev/null 2>&1 \
   && flatpak info io.github.berarma.Oversteer >/dev/null 2>&1 \
   && ls /dev/input/by-id/ 2>/dev/null | grep -qiE "wheel|racing"; then
    flatpak run io.github.berarma.Oversteer -p "\$WHEEL_PROFILE" >/dev/null 2>&1 || true
fi

export STEAM_COMPAT_CLIENT_INSTALL_PATH="$STEAM_ROOT"
export STEAM_COMPAT_DATA_PATH="$pfx"
export WINEDLLOVERRIDES="${overrides:+$overrides;}lsteamclient=d"
export DXVK_STATE_CACHE_PATH="$pfx/dxvk_cache"
export __GL_SHADER_DISK_CACHE=1
export __GL_SHADER_DISK_CACHE_PATH="$pfx/nv_cache"
mkdir -p "\$DXVK_STATE_CACHE_PATH" "\$__GL_SHADER_DISK_CACHE_PATH"

cd "\$GAME_DIR"
exec python3 "\$PROTON" run "\$TARGET" "\$@"
EOF
    chmod +x "$path"
    printf '%s' "$path"
}

extract_icon() {
    local dir="$1" id="$2"
    local ico
    ico=$(find "$dir" -maxdepth 1 -iname "*.ico" | head -1)
    [[ -n "$ico" ]] || { printf '%s' "applications-games"; return 0; }
    mkdir -p "$ICON_DIR"
    if convert "${ico}[0]" -resize 256x256 "$ICON_DIR/nfs-$id.png" 2>/dev/null; then
        printf '%s' "$ICON_DIR/nfs-$id.png"
    else
        printf '%s' "applications-games"
    fi
}

write_desktop_entry() {
    local id="$1" label="$2" exec_path="$3" icon="$4"
    mkdir -p "$APPS_DIR"
    local file="$APPS_DIR/nfs-$id.desktop"
    cat > "$file" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=$label
Comment=Classic Need for Speed running through Proton
Exec=$exec_path
Icon=$icon
Terminal=false
Categories=Game;ArcadeGame;
StartupNotify=true
StartupWMClass=steam_proton
EOF
    chmod +x "$file"
    local desktop_dir
    desktop_dir=$(xdg-user-dir DESKTOP 2>/dev/null || printf '%s' "$HOME/Desktop")
    if [[ -d "$desktop_dir" ]]; then
        cp "$file" "$desktop_dir/"
        chmod +x "$desktop_dir/nfs-$id.desktop"
        command -v gio >/dev/null 2>&1 && gio set "$desktop_dir/nfs-$id.desktop" metadata::trusted true 2>/dev/null || true
    fi
}

install_game() {
    local id="$1"
    load_game "$id" || { warn "unknown game id: $id"; return 0; }
    local pfx; pfx=$(prefix_path "$id")
    local dir="$pfx/pfx/drive_c/Games/$GAME_DIRNAME"

    if [[ "$TUNE_ONLY" -eq 1 ]]; then
        [[ -n "$(ls -A "$dir" 2>/dev/null)" ]] || return 0
        [[ "$id" == "prostreet" ]] && install_prostreet_fix "$dir"
        install_xtendedinput "$id" "$dir"
        tune_game "$dir"
        local rexe; rexe=$(detect_exe "$dir")
        if [[ -n "$rexe" ]]; then
            local rlauncher ricon
            rlauncher=$(write_launcher "$id" "$pfx" "$dir" "$rexe" "$GAME_OVERRIDES" "$GAME_LABEL")
            ricon=$(extract_icon "$dir" "$id")
            write_desktop_entry "$id" "$GAME_LABEL" "$rlauncher" "$ricon"
        fi
        ok "$GAME_LABEL retuned"
        return 0
    fi

    local zip; zip=$(find_zip "$GAME_ZIP_GLOB")
    [[ -n "$zip" ]] || { warn "skipping $GAME_LABEL, archive not found"; return 0; }

    if [[ -n "$(ls -A "$dir" 2>/dev/null)" ]]; then
        ok "$GAME_LABEL already installed, skipping"
    else
        create_prefix "$pfx"
        case "$GAME_KIND" in
            magipack|advinst) install_magipack "$id" "$zip" "$pfx" ;;
            isorepack) install_isorepack "$id" "$zip" "$pfx" ;;
            bundle7z) install_bundle7z "$id" "$zip" "$pfx" ;;
        esac
    fi

    [[ "$id" == "prostreet" ]] && install_prostreet_fix "$dir"
    install_xtendedinput "$id" "$dir"
    tune_game "$dir"

    local exe; exe=$(detect_exe "$dir")
    [[ -n "$exe" ]] || { fail "$GAME_LABEL: no executable found in $dir"; return 0; }

    local launcher icon
    launcher=$(write_launcher "$id" "$pfx" "$dir" "$exe" "$GAME_OVERRIDES" "$GAME_LABEL")
    icon=$(extract_icon "$dir" "$id")
    write_desktop_entry "$id" "$GAME_LABEL" "$launcher" "$icon"
    ok "$GAME_LABEL ready ($exe)"
}

summary() {
    log ""
    printf '%s%s%s\n\n' "$C_GREEN$C_BOLD" "Done." "$C_RESET"
    local id
    for id in "${SELECTED[@]}"; do
        load_game "$id" || continue
        local p="$GAMES_ROOT/nfs-$id-play.sh"
        [[ -x "$p" ]] && log "  $GAME_LABEL"$'\n'"    $p"
    done
    log ""
    log "  Shortcuts were added to your desktop and application menu."
    log "  Close Steam before playing or it will grab your controller."
    log ""
}

main() {
    parse_args "$@"
    printf '%s%s%s\n\n' "$C_BOLD" "$SCRIPT_NAME" "$C_RESET"
    [[ ${#SELECTED[@]} -gt 0 ]] || die "Pick something with --game <id> or --all (see --list)"
    discovery
    [[ "$CHECK_ONLY" -eq 1 ]] && exit 0
    [[ "$TUNE_ONLY" -eq 1 ]] || install_proton
    local id
    for id in "${SELECTED[@]}"; do install_game "$id"; done
    command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS_DIR" 2>/dev/null || true
    summary
}

main "$@"

# OpenForSpeed

Classic Need for Speed games running on Linux, with the widescreen fixes and graphics mods already in place.

These games came out between 1998 and 2008. None of them are sold anymore. The community keeps them alive with repacks and mods, and they run really well on Linux once you know the two or three settings that matter. This repo is those settings plus a script that does the boring parts.

![Main menu](screenshots/most-wanted.png)

## What works

| Game | Year | Status | Notes |
|---|---|---|---|
| Need for Speed Underground | 2003 | plays | widescreen fix, extra options |
| Need for Speed Underground 2 | 2004 | plays | widescreen fix, extra options |
| Need for Speed Most Wanted | 2005 | plays | widescreen, HD reflections, HUD adapter, DSOAL audio |
| Need for Speed Carbon | 2006 | plays | widescreen, HD reflections, HUD adapter, EA Trax in races |
| Need for Speed ProStreet | 2007 | crashes | this repack does not start, see below |
| Need for Speed Undercover | 2008 | plays | set the window mode to 4, then pick your resolution in game |
| Need for Speed III Hot Pursuit | 1998 | plays | keyboard only, the gamepad needs a mapper |
| Need for Speed Hot Pursuit 2 | 2002 | runs | set the resolution in a file first, see below |

Plays means somebody actually drove a race with a controller. Runs means it boots and renders but has not had a full session yet. If you get further with any of them, or get ProStreet going, open an issue and say how.

Tested on this machine:

| | |
|---|---|
| OS | Zorin OS 18.1 (Ubuntu 24.04 base) |
| Kernel | 7.0.0-28-generic |
| Desktop | GNOME on X11, triple monitor |
| CPU | AMD Ryzen 9 3900X, 24 threads |
| RAM | 62 GB |
| GPU | NVIDIA RTX 4070 Ti, driver 580.173.02 |
| Vulkan | 1.4.312 |
| Proton | GE-Proton11-3 |
| Controller | Xbox controller over USB |

Everything installs inside your home folder. No sudo, so this also works on Bazzite, SteamOS and other immutable systems.

## Getting the games

The games are abandonware. [myabandonware](https://www.myabandonware.com/search/q/need+for+speed/pla/4) has them.

Pick the **MagiPack** versions when there is a choice. They come with the official patch already applied plus ThirteenAG's fix pack, so you get widescreen, working controllers and better graphics without hunting down mods yourself. The repack notes inside each archive tell you exactly what is bundled.

The downloads are big and spread across file hosts with timers. [JDownloader](https://jdownloader.org/) handles that queue while you do something else:

```bash
flatpak install flathub org.jdownloader.JDownloader
```

Keep each game in its own folder and leave the archive names alone. The script finds games by their file names.

## Install

```bash
git clone https://github.com/<your-user>/openforspeed.git
cd openforspeed
./install.sh --list
./install.sh --source ~/Downloads --game most-wanted
```

Install several at once:

```bash
./install.sh --source ~/Downloads --game underground --game underground-2 --game most-wanted
```

Or everything it can find:

```bash
./install.sh --source ~/Downloads --all
```

Check your system without installing anything:

```bash
./install.sh --check --source ~/Downloads --all
```

```
==> Checking your system
  distro : Zorin OS 18.1
  kernel : 7.0.0-28-generic
  session: x11

  [ ok ] running as user, no root needed
  [ ok ] curl, tar, unzip, 7z and python3 are available
  [ ok ] GPU: NVIDIA Corporation AD104 [GeForce RTX 4070 Ti]
  [ ok ] Vulkan driver: 580.173.02
  [ ok ] Steam data found at /home/user/.steam/root
  [ ok ] GE-Proton11-3 already installed
  [ ok ] 97 GB free, selection needs about 52 GB
  [ ok ] Need for Speed Most Wanted: Need-for-Speed-Most-Wanted_Win_EN_MagiPack.zip

  [ ok ] discovery passed
```

The whole install runs unattended. The MagiPack installers accept `/VERYSILENT`, so there is no wizard to click through. When it finishes you get a launcher script in `~/Games` and shortcuts on your desktop and in your app menu.

## It configures the games for your hardware

Out of the box these games run at 800x600 with 2005 settings. The script looks at your machine and rewrites the mod config files so you get your real resolution and graphics that match what your GPU can do.

It reads your primary monitor from `xrandr`, your GPU vendor from `lspci`, and your VRAM from `nvidia-smi`, the AMD sysfs entries or `vulkaninfo`, whichever answers first. No extra tools to install, which matters on Bazzite and Steam Deck where you cannot just apt install something.

Three presets, picked from VRAM:

| Preset | VRAM | Shadow resolution | Reflection scale | Mirror shadows |
|---|---|---|---|---|
| high | 6 GB or more | 8192 | 2.0x | on |
| medium | 2 to 6 GB | 4096 | 1.5x | off |
| low | under 2 GB | 1024 | 1.0x | off |

It also sets your native resolution, turns on gamepad button icons if it finds a controller, and skips the intro videos.

Every comment in the ini files is left alone, so you can open them and tweak anything by hand afterwards. ThirteenAG documented each option right there in the file.

Redo the tuning any time, for example after changing monitors or GPUs:

```bash
./install.sh --tune-only --all
```

Or skip it entirely and keep the mod defaults:

```bash
./install.sh --source ~/Downloads --all --no-tune
```

### One open question

The widescreen fix has a `ForcedGPUVendor` setting that tells the game which GPU brand it is talking to. The script sets it to your real GPU.

The thing is, DXVK hides your real GPU from the game and reports an AMD device by default. So the value that is actually correct under Proton might be `0x1002` no matter what card you own. I could not test that properly with only an NVIDIA card here, and on NVIDIA the mod default already matches, so nothing changes either way. If you have an AMD or Intel card and notice a difference, please tell me.

## The two settings that actually matter

If you would rather set this up by hand, this is the short version.

**1. Load the mods with a DLL override.**

ThirteenAG's fixes ride on Ultimate ASI Loader, which ships as a fake `dinput8.dll` in the game folder. Wine loads its own `dinput8` unless you tell it not to, and then the game starts with no widescreen, no HD reflections and no controller fixes. It looks like the mods were never installed.

```bash
WINEDLLOVERRIDES="dinput8=n,b"
```

Most Wanted also ships DSOAL for positional audio, which hides behind `dsound.dll`:

```bash
WINEDLLOVERRIDES="dinput8=n,b;dsound=n,b"
```

**2. Use GE-Proton, not plain Wine.**

DXVK turns the DirectX 9 calls into Vulkan and these games fly. GE-Proton11-3 ships DXVK 3.0.2 and that combination is what got tested here.

One thing to know: [DXVK 2.5.2 and 2.5.3 break Most Wanted](https://github.com/doitsujin/dxvk/issues/4624) with an access violation on startup. If you are on an older Proton and the game dies before the menu, that is probably why. 3.0.2 is fine.

Verify the mods actually loaded instead of assuming:

```bash
pgrep -x speed.exe | while read p; do tr '\0' '\n' < /proc/$p/maps; done | grep -oiE "[^/]*\.asi" | sort -u
```

You should see the `.asi` files listed. If that comes back empty, your override is not applied.

## Controller

**Close Steam before you play.** Steam Input takes exclusive control of the gamepad. The game still lists the controller but never gets a button press, so it looks broken when it is not. The launchers warn you if Steam is running.

If you want Steam open anyway, turn off Xbox controller support in Steam Settings, Controller.

## Per game notes

**Most Wanted** ships DSOAL for better audio. There are presets in `~DSOAL` inside the game folder if you want to mess with them.

**Underground 2** had its soundtrack restored in repack v4. If you want the original censored one, delete `pfdata` and `speech` in the game folder and rename `SDATA.Backup` to `SDATA`.

**Undercover** includes NFS VltEd in the game folder if you want to get into modding the game files.

**Undercover** opens in a tiny window because the repack ships `WindowedMode = 1`. Set it to `4` in `scripts/NFSUndercover.GenericFix.ini` for borderless fullscreen, which the script now does for you. After that, open the video options in game and pick your resolution. The game boots at 1920x1080 and on a multi monitor setup it will land on whichever screen matches, not necessarily your main one.

**ProStreet** does not run with this repack. It crashes on startup every time, always at the same address:

```
Unhandled page fault on write access to 0x00007077 at address 0x01F6880E, wow64 32-bit code
```

Things that did not change anything:

- GE-Proton11-3 with DXVK
- GE-Proton11-3 with DXVK off (`PROTON_USE_WINED3D=1`)
- Plain wine-staging 11.14
- Removing every mod by renaming `dinput8.dll`
- Adding the `d3dx9_34=n,b` override that people recommend for this game

Same crash, same address, every time, including with no mods at all. So it is the game executable, not Wine and not the mod stack.

Other people do run ProStreet on Linux, but with a different build. The [r/linux_gaming thread](https://www.reddit.com/r/linux_gaming/) that covers it uses a version whose executable is `nfs.exe`, while this repack ships `nfsps.exe`. Comments there point at needing a Wine friendly patched executable, which the [Pepega Mod](https://pepegamod.com/pepega-download/) includes. If you get another build working, please open an issue and say which one.

**NFS III** is not a normal install. It is the [Modern Bundle by Evgeny Vrublevsky](http://veg.by/en/projects/nfs3/), which is a rewritten version with widescreen, multi core support and no registry use. The script just extracts it and sets `nfs3.ini` for you.

The game runs great but it cannot see your gamepad. It is from 1998 and only speaks DirectInput, while Wine hands modern controllers to XInput. Open `control joy.cpl` in the prefix and you can see it yourself: the controller sits under "XInput devices" and the "DirectInput devices" list is empty.

Turning off SDL in `winebus` does not fix it, it makes it worse. Xbox pads use the `xpad` kernel driver, which creates evdev nodes and no hidraw node, so with SDL off Wine loses the controller completely and both lists come up empty. Tested, do not bother.

What does work is mapping the pad to the keyboard, which is the usual answer for pre 2000 games:

```bash
flatpak install flathub io.github.antimicrox.antimicrox
```

Open AntiMicroX, pick your controller, and bind the sticks and triggers to the arrow keys plus whatever else you want. NFS III has full keyboard support and its own Controllers menu shows you the current key bindings. Leave AntiMicroX running while you play.

**Hot Pursuit 2** works, and the DirectPlay warning in its readme turned out to be a red herring. Wine ships its own `dplay.dll` and `dplayx.dll`, and if you trace the running game you can see DirectPlay is never even loaded. It is only needed for LAN play.

Two things are specific to this one:

It is a DirectX 8 game and the repack ships a `d3d8.dll` wrapper, so it needs its own override. The launcher sets it:

```
WINEDLLOVERRIDES="d3d8=n,b;dinput8=n,b"
```

The chain ends up being the game, then the d3d8 wrapper, then d3d9 through DXVK, then Vulkan. Sounds fragile, runs fine.

Its resolution is not in the game menu. Edit this file and set both `[Graphics]` and `[GraphicsFE]`:

```
~/Games/nfs-hot-pursuit-2/pfx/drive_c/users/steamuser/Documents/EA Games/Need For Speed Hot Pursuit 2/rendercaps.ini
```

```ini
Width=3440
Height=1440
```

Like NFS III it loads the old `dinput.dll`, so a gamepad probably needs AntiMicroX too.

## If something breaks

**Game opens but looks like the mods are missing**

Your `dinput8` override is not applied. See above.

**Game window is black in a screenshot but fine on screen**

That is a screenshot problem, not a game problem. `import -window <id>` cannot read a Vulkan surface and gives you a black image. Capture the whole screen and crop instead:

```bash
import -window root shot.png
```

**Moved the game folder and the uninstaller broke**

The Inno Setup installers write the install path into the registry. If you move the folder you have to update those keys too.

Read the registry with the prefix shut down, otherwise you get stale results. Wine keeps the registry in memory and only writes `system.reg` and `user.reg` now and then, so grepping those files while the game or the installer is running can show you nothing when there is plenty there. Kill `wineserver` first.

**A `pkill -f` command killed your own terminal**

`pkill -f` matches the full command line, including the shell that is running your script. Use `pkill -x` with the exact process name.

**Doing it by hand and the silent install returns 1**

Use `/VERYSILENT`, not `/SILENT`. This is the full line that works:

```bash
proton run Setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART "/DIR=C:\\Games\\NFSMW"
```

`/SILENT` still draws a progress window and it did not survive being started from a script here. `/VERYSILENT` draws nothing and exits 0. Add `/LOG=C:\inno.log` if you want to see what it did, the log lands inside the prefix and lists every file.

**Each game has a different executable name**

`speed.exe`, `SPEED2.EXE`, `Speed.exe`, and so on, with different capitalization too. The script finds the biggest `.exe` in the game folder instead of keeping a list, which is why it works on games nobody has tested yet. Worth knowing if you write your own launcher.

## Where everything goes

```
~/Games/
├── nfs-most-wanted/           prefix, game in pfx/drive_c/Games/NFSMW
├── nfs-underground-2/         prefix, game in pfx/drive_c/Games/NFSU2
├── nfs-most-wanted-play.sh    launcher
├── nfs-underground-2-play.sh  launcher
└── _installers/nfs/           unpacked archives
```

`_installers/nfs` keeps the unpacked archives so a reinstall does not have to read your USB drive again. It adds up fast, around 8 GB for four games. Delete it whenever you want, nothing depends on it once the games are installed:

```bash
rm -rf ~/Games/_installers/nfs
```

One prefix per game on purpose. These are old games with mods that hook into system DLLs, and keeping them apart means a broken mod in one cannot take down another.

To remove a game, delete its prefix folder, its launcher and the two `.desktop` files.

## Credits

**[MagiPack](https://www.magipack.games/)** put together the repacks, with the official patches and the mods already wired up. Most of the work here was already done by them.

**[ThirteenAG](https://github.com/ThirteenAG/WidescreenFixesPack)** wrote the widescreen fixes and Ultimate ASI Loader that make these games playable on modern screens.

**[Evgeny Vrublevsky](http://veg.by/en/projects/nfs3/)** for the NFS III Modern Patch.

**[GloriousEggroll](https://github.com/GloriousEggroll/proton-ge-custom)** for GE-Proton.

**Bladez1992 and Legacy Gamers' Union** for the Hot Pursuit 2 repack, and **[xan1242](https://github.com/xan1242/hp2wsfix)** for hp2wsfix.

I only worked out the Linux side and wrote it down.

## Contributing

Got one of the untested games running? Or Hot Pursuit 2? Open an issue with your distro, GPU and what you changed. Reports from Bazzite and Steam Deck are especially welcome.

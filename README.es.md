# OpenForSpeed

**Juega los Need for Speed clásicos en Linux.** Ocho de ellos, con los parches de pantalla ancha y los mods gráficos ya configurados, mando y volante funcionando, un solo script y sin sudo.

> Underground · Underground 2 · Most Wanted · Carbon · ProStreet · Undercover · NFS III Hot Pursuit · Hot Pursuit 2

**Léelo en otros idiomas:** [English](README.md) · [Português do Brasil](README.pt-BR.md)

Probado en sistemas basados en Ubuntu y en Fedora, y hecho para funcionar también en **Bazzite, SteamOS y Steam Deck**, donde no puedes instalar nada a nivel de sistema. Todo queda dentro de tu carpeta personal.

Estos juegos salieron entre 1998 y 2008. Ninguno se vende ya. La comunidad los mantiene vivos con repacks y mods, y corren muy bien en Linux una vez que sabes las dos o tres opciones que importan. Este repositorio es esas opciones más un script que hace la parte aburrida.

Si esto te ayuda a hacer funcionar alguno, una estrella le facilita la vida a la siguiente persona que busque.

![Hot Pursuit 2 corriendo en Linux a 3440x1440](screenshots/hot-pursuit-2.png)

## Qué funciona

| Juego | Año | Estado | Notas |
|---|---|---|---|
| Need for Speed Underground | 2003 | se juega | pantalla ancha, opciones extra |
| Need for Speed Underground 2 | 2004 | se juega | pantalla ancha, opciones extra |
| Need for Speed Most Wanted | 2005 | se juega | pantalla ancha, reflejos en HD, HUD adaptado, audio DSOAL |
| Need for Speed Carbon | 2006 | se juega | pantalla ancha, reflejos en HD, HUD adaptado, EA Trax en carreras |
| Need for Speed ProStreet | 2007 | se juega | usa el repack de ElAmigos, no el MagiPack |
| Need for Speed Undercover | 2008 | se juega | pon el modo de ventana en 4 y elige la resolución dentro del juego |
| Need for Speed III Hot Pursuit | 1998 | se juega | solo teclado, el mando necesita un mapeador |
| Need for Speed Hot Pursuit 2 | 2002 | se juega | fuerza el d3d8 integrado, explicado abajo |

Se juega significa que alguien corrió una carrera completa con mando. Arranca significa que abre y dibuja en pantalla, pero todavía no tuvo una sesión completa. Si llegas más lejos con alguno, abre un issue y cuenta cómo.

Probado en esta máquina:

| | |
|---|---|
| Sistema | Zorin OS 18.1 (base Ubuntu 24.04) |
| Kernel | 7.0.0-28-generic |
| Escritorio | GNOME en X11, tres monitores |
| CPU | AMD Ryzen 9 3900X, 24 hilos |
| RAM | 62 GB |
| GPU | NVIDIA RTX 4070 Ti, driver 580.173.02 |
| Vulkan | 1.4.312 |
| Proton | GE-Proton11-3 |
| Mando | Xbox por USB |

Todo se instala dentro de tu carpeta personal. Sin sudo, así que también funciona en Bazzite, SteamOS y otros sistemas inmutables.

## Consiguiendo los juegos

Todos vinieron de [myabandonware](https://www.myabandonware.com/search/q/need+for+speed/pla/4). Busca el juego, abre su página y toma exactamente el archivo listado abajo. El script encuentra cada juego por el nombre del archivo, así que descárgalos y no los renombres.

| Juego | Archivo |
|---|---|
| Underground | `Need-for-Speed-Underground_Win_EN_MagiPack.zip` |
| Underground 2 | `Need-for-Speed-Underground-2_Win_EN_MagiPack.zip` |
| Most Wanted | `Need-for-Speed-Most-Wanted_Win_EN_MagiPack.zip` |
| Carbon | `Need-for-Speed-Carbon_Win_EN_MagiPack.zip` |
| ProStreet | `Need-for-Speed-ProStreet_Win_EN-FR-DE-IT-ES-NL-DA-FI-SV-HU-CS-PL-RU_Repack.zip` |
| Undercover | `Need-for-Speed-Undercover_Win_EN-FR-DE-IT-ES-NL-SV-DA-FI-PL-RU-CS-HU_Repack.zip` |
| NFS III Hot Pursuit | `Need-for-Speed-III-Hot-Pursuit_Win_EN-FR-ES-DE-IT_Modern-Bundle.zip` |
| Hot Pursuit 2 | `Need-for-Speed-Hot-Pursuit-2_Win_EN_LGU-Repack-by-Bladez1992.zip` |

Estas son exactamente las versiones contra las que se probó todo aquí. Otras ediciones del mismo juego pueden funcionar, pero estas son las que sé que funcionan.

### ProStreet es la excepción

No uses `Need-for-Speed-ProStreet_Win_EN_MagiPack.zip`. Lo probé primero, porque las compilaciones MagiPack son la mejor opción para todos los demás juegos, y falla al arrancar todas las veces con el mismo page fault. Los detalles están más abajo.

El repack de ElAmigos de la tabla de arriba arranca sin drama. Trae el juego limpio, sin mods, y el script descarga el parche de pantalla ancha durante la instalación.

### Descargando

Los archivos son grandes y los servidores tienen tiempos de espera. [JDownloader](https://jdownloader.org/) los pone en cola y se encarga de la espera mientras haces otra cosa:

```bash
flatpak install flathub org.jdownloader.JDownloader
```

Pon todo en una sola carpeta. El script busca de forma recursiva, así que las subcarpetas no son problema.

## Instalación

```bash
git clone https://github.com/agentkyo/openforspeed.git
cd openforspeed
./install.sh --list
./install.sh --source ~/Downloads --game most-wanted
```

Instalar varios a la vez:

```bash
./install.sh --source ~/Downloads --game underground --game underground-2 --game most-wanted
```

O todo lo que encuentre:

```bash
./install.sh --source ~/Downloads --all
```

Revisar tu sistema sin instalar nada:

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

La instalación completa corre sola. Los instaladores MagiPack aceptan `/VERYSILENT`, así que no hay asistente que clicar. Cuando termina te quedas con un script lanzador en `~/Games` y accesos directos en el escritorio y en el menú de aplicaciones.

## Configura los juegos para tu hardware

Tal como vienen, estos juegos corren a 800x600 con ajustes de 2005. El script mira tu máquina y reescribe los archivos de configuración de los mods para que tengas tu resolución real y gráficos acordes a lo que aguanta tu GPU.

Lee tu monitor principal con `xrandr`, el fabricante de la GPU con `lspci`, y la VRAM con `nvidia-smi`, con las entradas sysfs de AMD o con `vulkaninfo`, lo que responda primero. Ninguna herramienta extra que instalar, lo que importa en Bazzite y Steam Deck, donde no puedes simplemente instalar un paquete.

Tres perfiles, elegidos por VRAM:

| Perfil | VRAM | Resolución de sombras | Escala de reflejos | Sombras en espejos |
|---|---|---|---|---|
| high | 6 GB o más | 8192 | 2.0x | activado |
| medium | 2 a 6 GB | 4096 | 1.5x | desactivado |
| low | menos de 2 GB | 1024 | 1.0x | desactivado |

También pone tu resolución nativa, activa los iconos de botones de mando si encuentra uno conectado, y salta los vídeos de intro.

Todos los comentarios de los archivos ini quedan intactos, así que puedes abrirlos y ajustar lo que quieras después. ThirteenAG documentó cada opción ahí mismo dentro del archivo.

Además de los perfiles, activa todo lo que no cuesta nada y solo mejora el juego: correcciones de sombras, reflejos con más detalle, HUD escalado para ultrapanorámico, tasa de fotogramas liberada en los juegos que lo soportan, las protecciones contra fallos que incluye ThirteenAG, y saltar los vídeos de intro.

Rehaz el ajuste cuando quieras, por ejemplo después de cambiar de monitor o de GPU:

```bash
./install.sh --tune-only --all
```

O sáltatelo por completo y quédate con los valores por defecto de los mods:

```bash
./install.sh --source ~/Downloads --all --no-tune
```

### Una duda abierta

El parche de pantalla ancha tiene una opción `ForcedGPUVendor` que le dice al juego con qué marca de GPU está hablando. El script pone tu GPU real.

El detalle es que DXVK esconde tu GPU real del juego y reporta un dispositivo AMD por defecto. Así que el valor realmente correcto bajo Proton quizá sea `0x1002` sin importar qué tarjeta tengas. No pude probarlo bien con solo una NVIDIA aquí, y en NVIDIA el valor por defecto del mod ya coincide, así que no cambia nada de ninguna manera. Si tienes una AMD o Intel y notas diferencia, cuéntame.

## Las dos opciones que de verdad importan

Si prefieres montarlo a mano, esta es la versión corta.

**1. Carga los mods con un override de DLL.**

Los parches de ThirteenAG van montados sobre Ultimate ASI Loader, que llega como un `dinput8.dll` falso en la carpeta del juego. Wine carga el suyo propio a menos que le digas lo contrario, y entonces el juego arranca sin pantalla ancha, sin reflejos en HD y sin las correcciones de mando. Parece que los mods nunca se instalaron.

```bash
WINEDLLOVERRIDES="dinput8=n,b"
```

Most Wanted también trae DSOAL para audio posicional, que se esconde detrás de `dsound.dll`:

```bash
WINEDLLOVERRIDES="dinput8=n,b;dsound=n,b"
```

**2. Usa GE-Proton, no Wine a secas.**

DXVK convierte las llamadas de DirectX 9 a Vulkan y estos juegos vuelan. GE-Proton11-3 trae DXVK 3.0.2 y esa es la combinación que se probó aquí.

Algo que conviene saber: [DXVK 2.5.2 y 2.5.3 rompen Most Wanted](https://github.com/doitsujin/dxvk/issues/4624) con una violación de acceso al arrancar. Si estás en un Proton más viejo y el juego muere antes del menú, probablemente sea eso. La 3.0.2 va bien.

Verifica que los mods cargaron en vez de suponerlo:

```bash
pgrep -x speed.exe | while read p; do tr '\0' '\n' < /proc/$p/maps; done | grep -oiE "[^/]*\.asi" | sort -u
```

Deberías ver los archivos `.asi` en la lista. Si sale vacío, tu override no se está aplicando.

## Mando

Undercover llegó con el mejor manejo de mando del grupo, así que el script le da esa misma configuración a los demás.

Viene de [NFS-XtendedInput](https://github.com/xan1242/NFS-XtendedInput) de xan1242, que reemplaza el código de entrada viejo por XInput de verdad. Consigues iconos de botones correctos, sticks y gatillos funcionando, y el juego se pausa cuando desconectas el mando, como en consola. El script lo descarga y lo instala para Most Wanted, Carbon, ProStreet y Undercover, y luego pone las mismas zonas muertas en todos:

```ini
PercentLS = 0.24                    stick izquierdo
PercentRS = 0.24                    stick derecho
Percent_Shifting = 0.75             cuánto recorre un gatillo antes de contar
Percent_AnalogStickDigital = 0.50   stick como cruceta
PassConnStatus = 1                  pausa cuando el mando se desconecta
```

Underground y Underground 2 no tienen compilación de XtendedInput, así que usan `ImproveGamepadSupport` de ThirteenAG, que el script también activa. Funciona bien, solo tiene menos ajustes.

### Mando o volante, tienes que elegir

XtendedInput lo dice claramente en su propio readme: **"Currently KILLS Direct Input, beware"**. DirectInput es por donde aparecen los volantes, así que con XtendedInput instalado tu volante desaparece de esos cuatro juegos.

Por eso hay dos modos:

```bash
./install.sh --source ~/Downloads --all                  # mando, el predeterminado
./install.sh --source ~/Downloads --all --input wheel    # volante
```

Cambia después sin reinstalar nada:

```bash
./install.sh --tune-only --all --input wheel
./install.sh --tune-only --all --input gamepad
```

Solo renombra el archivo `.asi`, así que ir y volver toma un segundo.

Underground, Underground 2, NFS III y Hot Pursuit 2 no se ven afectados de ninguna forma. Nunca reciben XtendedInput, así que un volante funciona en los cuatro sin importar el modo que elijas.

Una cosa más sobre Most Wanted: con XtendedInput activo, el menú de Controles dentro del juego queda deshabilitado porque hace fallar el juego. Es el mod haciéndolo a propósito. Usa el modo volante si necesitas ese menú.

Un apunte para quien lo instale a mano: XtendedInput y el parche de ThirteenAG traen ambos un `dinput8.dll`, y si dejas que uno sobrescriba al otro te queda un juego que no arranca. Los dos son el mismo cargador ASI, y carga cada `.asi` de la carpeta `scripts/`, así que quédate con un solo `dinput8.dll` y pon los dos `.asi` uno junto al otro. Es lo que hace el script.

**Cierra Steam antes de jugar.** Steam Input toma control exclusivo del mando. El juego sigue listando el mando pero nunca recibe un botón, así que parece roto sin estarlo. Los lanzadores te avisan si Steam está abierto. Si quieres tener Steam abierto igual, desactiva el soporte de mando Xbox en Configuración, Mando.

### Los volantes funcionan mejor que los mandos en los juegos viejos

Si tienes un volante, úsalo. Un Logitech G29 aparece en DirectInput, que es exactamente donde miran los dos juegos viejos y exactamente donde un mando de Xbox nunca aparece:

```
Connected (DirectInput devices)
  Logitech G29 Driving Force Racing Wheel

Connected (XInput devices)
  Controller (Xbox One For Windows)
```

Todo el problema está en esa captura. NFS III y Hot Pursuit 2 son de 1998 y 2002, cuando un volante DirectInput era la forma normal de jugar carreras, así que ven el volante sin problema mientras el mando moderno les es invisible.

Nada que instalar del lado de Wine. Si el kernel ve el volante, el juego también. Comprueba con:

```bash
ls /dev/input/by-id/ | grep -i wheel
lsmod | grep -E "hid_logitech|ff_memless"
```

Que `ff_memless` esté cargado significa que el force feedback está disponible.

### Combina los pedales o los juegos se vuelven locos

Un G29 reporta acelerador, freno y embrague como tres ejes separados que se quedan en su valor máximo cuando no los pisas. Los juegos de esa época esperan un solo eje de pedal centrado en cero, así que leen ese valor en reposo como entrada máxima. El resultado es Hot Pursuit 2 acelerando solo antes de que toques nada, y ProStreet bajando por su menú sin parar hasta que pisas el embrague y sin querer devuelves el eje al centro.

El arreglo es una sola opción:

```bash
flatpak install flathub io.github.berarma.Oversteer
flatpak run io.github.berarma.Oversteer --combine-pedals 1 --range 270
```

Oversteer no puede tocar el volante hasta que le des permiso, y no instala la regla de udev por sí mismo:

```bash
sudo curl -o /etc/udev/rules.d/99-logitech-wheel-perms.rules \
  https://raw.githubusercontent.com/berarma/oversteer/master/data/udev/99-logitech-wheel-perms.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Desconecta el volante y vuelve a conectarlo. Este es el único comando de toda esta guía que necesita sudo.

### Un perfil por juego

El script escribe un perfil de Oversteer para cada juego y los lanzadores lo cargan antes de que arranque, así el volante queda bien sin que pienses en ello. La rotación es más cerrada en los juegos arcade y más abierta en ProStreet, y el force feedback es más fuerte en los viejos, donde los efectos son más toscos.

| Juego | Rotación |
|---|---|
| NFS III, Hot Pursuit 2 | 270 |
| Underground, Underground 2, Most Wanted, Carbon | 270 |
| Undercover | 300 |
| ProStreet | 360 |

Todos usan `combine_pedals = 1`. Edita cualquiera en Oversteer y tus cambios se quedan, los lanzadores solo cargan lo que diga el perfil.

Los perfiles también llevan valores de autocentrado, ganancia, muelle y amortiguación, pero comprueba si tu volante los acepta antes de gastar tiempo ajustando. En un G29 con el driver estándar del kernel, solo existen tres archivos:

```bash
ls /sys/bus/hid/devices/*046D*/ | grep -E "range|combine|alternate"
```

Son `range`, `combine_pedals` y `alternate_modes`. Los ajustes de intensidad del force feedback necesitan [new-lg4ff](https://github.com/berarma/new-lg4ff), que reemplaza el driver estándar. Sin él esos valores se escriben en el perfil, Oversteer los acepta, y no pasa nada. El force feedback en sí sigue funcionando, simplemente no puedes ajustar su fuerza desde aquí.

Instala new-lg4ff si quieres ese control. Las dos opciones que arreglan los problemas reales, combinar los pedales y cerrar la rotación, funcionan bien con el driver estándar.

### Los dos viejos

NFS III y Hot Pursuit 2 son de 1998 y 2002 y solo hablan el DirectInput antiguo. Wine entrega los mandos modernos a XInput, así que estos dos o no ven nada o ven algo para lo que no tienen perfil.

Hot Pursuit 2 sí ve el mando. Dice que no lo reconoce y te manda a Controller Options, donde puedes mapear los botones tú mismo. Hazlo y funciona durante las carreras, pero los menús se quedan solo con teclado. Un volante no tiene este problema.

NFS III no ve nada en absoluto. Mapea el mando al teclado:

```bash
flatpak install flathub io.github.antimicrox.antimicrox
```

Asigna los sticks y gatillos a las flechas, déjalo corriendo, y juega. El menú Controllers del propio juego te muestra qué tecla hace qué.

No intentes desactivar SDL en `winebus` para forzar DirectInput. Lo probé y empeora las cosas. Los mandos de Xbox usan el driver `xpad` del kernel, que da nodos evdev y ningún nodo hidraw, así que con SDL apagado Wine pierde el mando por completo.

## Notas por juego

**Most Wanted** trae DSOAL para mejor audio. Hay perfiles en `~DSOAL` dentro de la carpeta del juego si quieres trastear.

**Underground 2** recuperó su banda sonora en el repack v4. Si quieres la original censurada, borra `pfdata` y `speech` en la carpeta del juego y renombra `SDATA.Backup` a `SDATA`.

**Undercover** incluye NFS VltEd en la carpeta del juego por si quieres meterte a modificar los archivos.

**Undercover** abre en una ventana diminuta porque el repack trae `WindowedMode = 1`. Ponlo en `4` en `scripts/NFSUndercover.GenericFix.ini` para pantalla completa sin bordes, que es lo que el script ya hace por ti. Después de eso, abre las opciones de vídeo dentro del juego y elige tu resolución. El juego arranca a 1920x1080 y en un montaje de varios monitores va a caer en el que coincida, no necesariamente el principal.

**ProStreet** funciona, pero solo con el repack de ElAmigos. El MagiPack falla al arrancar todas las veces, siempre en la misma dirección:

```
Unhandled page fault on write access to 0x00007077 at address 0x01F6880E, wow64 32-bit code
```

Cosas que no cambiaron nada:

- GE-Proton11-3 con DXVK
- GE-Proton11-3 con DXVK apagado (`PROTON_USE_WINED3D=1`)
- wine-staging 11.14 a secas
- Quitar todos los mods renombrando `dinput8.dll`
- Añadir el override `d3dx9_34=n,b` que recomiendan para este juego

Mismo fallo, misma dirección, todas las veces, incluso sin ningún mod. Así que es el ejecutable del juego, no Wine ni la pila de mods.

Otra gente sí corre ProStreet en Linux, pero con una compilación distinta. El [hilo de r/linux_gaming](https://www.reddit.com/r/linux_gaming/) que lo trata usa una versión cuyo ejecutable es `nfs.exe`, mientras que este repack trae `nfsps.exe`. Los comentarios de ahí apuntan a que hace falta un ejecutable parcheado para Wine, que el [Pepega Mod](https://pepegamod.com/pepega-download/) incluye. Si haces funcionar otra compilación, abre un issue y di cuál.

**NFS III** no es una instalación normal. Es el [Modern Bundle de Evgeny Vrublevsky](http://veg.by/en/projects/nfs3/), que es una versión reescrita con pantalla ancha, soporte multinúcleo y sin uso del registro. El script solo lo extrae y ajusta `nfs3.ini` por ti.

El juego corre genial, pero no ve tu mando. Es de 1998 y solo habla DirectInput, mientras que Wine entrega los mandos modernos a XInput. Abre `control joy.cpl` en el prefijo y lo ves tú mismo: el mando está bajo "XInput devices" y la lista "DirectInput devices" está vacía.

Desactivar SDL en `winebus` no lo arregla, lo empeora. Los mandos de Xbox usan el driver `xpad`, que crea nodos evdev y ningún hidraw, así que con SDL apagado Wine pierde el mando por completo y las dos listas salen vacías. Probado, no pierdas el tiempo.

Lo que sí funciona es mapear el mando al teclado, que es la respuesta habitual para juegos anteriores al 2000:

```bash
flatpak install flathub io.github.antimicrox.antimicrox
```

Abre AntiMicroX, elige tu mando, y asigna los sticks y gatillos a las flechas más lo que quieras. NFS III tiene soporte completo de teclado y su propio menú Controllers te muestra las teclas actuales. Deja AntiMicroX corriendo mientras juegas.

**Hot Pursuit 2** funciona, y el aviso sobre DirectPlay en su readme resultó ser una pista falsa. Wine trae su propio `dplay.dll` y `dplayx.dll`, y si rastreas el juego en ejecución ves que DirectPlay ni siquiera se carga. Solo hace falta para jugar en red local.

Dos cosas son específicas de este:

Es un juego DirectX 8 y el repack trae su propio wrapper `d3d8.dll`, que traduce D3D8 a D3D9. Deja correr ese wrapper y el escenario se ve bien, pero todos los coches salen sin texturas, azul y rojo planos, con un bloque magenta sobre la pantalla de selección de coche. El magenta es el color clásico de textura ausente, y eso es exactamente lo que es.

Dile a Wine que use su propio d3d8 y los coches vuelven con texturas:

```
WINEDLLOVERRIDES="d3d8=b;dinput8=n,b"
```

Fíjate en la `b` sola, no `n,b`. Eso significa solo el integrado, así que el archivo del wrapper puede quedarse donde está y Wine simplemente lo ignora. Esto te deja en wined3d en vez de DXVK, lo que para un juego de 2002 no es problema.

Hacer esto también desactiva HP2WSFix, ya que era ese wrapper el que lo cargaba. El juego sigue corriendo a la resolución que pongas y la imagen no queda estirada, así que no pierdes mucho.

Su resolución no está en el menú del juego. Edita este archivo y ajusta tanto `[Graphics]` como `[GraphicsFE]`:

```
~/Games/nfs-hot-pursuit-2/pfx/drive_c/users/steamuser/Documents/EA Games/Need For Speed Hot Pursuit 2/rendercaps.ini
```

```ini
Width=3440
Height=1440
```

Sobre el mando: el juego saca "Your controller is not specifically recognized" y te manda a Controller Options. Sí ve el mando, solo que no tiene perfil para un Xbox porque el juego es anterior. Mapea los botones tú mismo en Controller Options, o usa AntiMicroX como con NFS III.

## La herramienta de entrada

Todo lo de arriba configura el volante a través del driver, y eso solo llega hasta cierto punto. Algunos de estos juegos leen los valores crudos de los ejes e ignoran la zona muerta que reporta el kernel, así que un pedal de embrague que descansa en su valor máximo se lee como una dirección de menú mantenida, sin importar lo que configures. Cambiar el volante a un modo de compatibilidad más viejo sí silencia ese pedal, pero entonces el volante aparece como otro dispositivo y todas las asignaciones que guardaste en el juego dejan de funcionar.

`tools/ofs_input.py` toma otro camino. Lee el volante o el mando real, aplica tus ajustes, y publica un segundo dispositivo virtual construido desde cero. El juego solo ve ese.

```bash
python3 tools/ofs_input.py list
python3 tools/ofs_input.py monitor
python3 tools/ofs_input.py calibrate --profile wheel
python3 tools/ofs_input.py bridge --profile wheel
```

`list` muestra cada dispositivo con sus ejes y marca los que descansan fuera del centro, que es lo que provoca menús descontrolados. `monitor` dibuja barras en vivo para que veas lo que hace cada pedal de verdad. `calibrate` te guía por cada eje: conservarlo o descartarlo, invertirlo, poner una zona muerta. `bridge` entonces ejecuta el dispositivo virtual.

Lo que ganas con esto:

- **El force feedback sigue funcionando.** El puente declara los mismos efectos que soporta el volante real y los reenvía, traduciendo los identificadores de efecto en ambos sentidos. Sin esto el juego muestra el force feedback como no disponible, ya que un dispositivo virtual que solo envía ejes y botones no puede recibir efectos.
- **Intensidad del force feedback ajustable.** El driver estándar `hid-logitech` no tiene control de ganancia, así que Oversteer no puede cambiarla. El puente escala la magnitud del efecto al pasar, lo que funciona con cualquier driver. Ponla durante la calibración, 100 mantiene lo que pida el juego.
- **Descartar un eje por completo.** El embrague nunca llega al juego, así que no puede mantener una dirección de menú.
- **Zonas muertas que funcionan.** Se aplican antes de enviar el evento, así que el juego recibe un valor ya limpio en lugar de tener que respetar una sugerencia.
- **Inversión por eje**, para pedales conectados al revés.
- **Una identidad de dispositivo estable.** El dispositivo virtual siempre tiene el mismo nombre, así que tus asignaciones dentro del juego sobreviven a desconexiones, cambios de modo y al cambio entre PS3 y PS4. Esta es la parte que más importa. Cambiar el modo del volante para arreglar el embrague costó un remapeo completo una vez.

No necesita root ni paquetes. `/dev/uinput` ya es escribible por tu usuario en la mayoría de escritorios, y todo es biblioteca estándar, lo que también significa que funciona en Bazzite y SteamOS, donde no puedes instalar paquetes de Python a nivel de sistema.

El rango de rotación, el force feedback y los pedales combinados siguen siendo cosa de Oversteer. Los dos trabajan juntos: Oversteer prepara el hardware, esta herramienta moldea lo que lee el juego.

### Eligiendo tu dispositivo cuando arranca un juego

Los lanzadores abren un menú antes del juego:

```
  OpenForSpeed   prostreet
  ==========================================================

   1  Wheel     Logitech G29 Driving Force Rac   calibrated (6 axes, 1 dropped)
   2  Gamepad   Xbox One For Windows             not calibrated yet
   3  Keyboard                                   no setup needed

  c calibrate    d delete a profile    f forget saved choice
  q quit

  starting with wheel in 5s  [#####...]
  press any listed key to stop the countdown
```

Cada opción te dice si existe un perfil y qué hay dentro, así sabes con qué vas a jugar. Si algún eje descansa fuera del centro te avisa ahí mismo, porque eso es lo que hace que los menús se desplacen solos.

La cuenta atrás solo corre cuando ya elegiste algo para ese juego antes. Cualquier tecla la detiene. Elige una opción que aún no tiene perfil y calibra primero, en vez de arrancar algo a medio configurar.

Volante y mando mantienen perfiles separados, así puedes configurar los dos y alternar por juego. `c` calibra cualquiera, `d` borra cualquiera, `f` limpia la elección guardada para ese juego.

## Cómo guarda cada juego sus asignaciones

Vale la pena saberlo antes de gastar una noche intentando editar el archivo equivocado.

**Hot Pursuit 2** es el único completamente abierto. `Controllers/definitions.ini` describe cada dispositivo, incluido dónde descansa cada eje:

```ini
axis0 = 0,left,127,0,kTxtAxis0Left
```

Eso es el eje 0, dirección izquierda, descansando en 127, extremo en 0. Acertar ese valor de reposo es exactamente lo que evita que un pedal se lea como pisado. `Controllers/defaults.ini` entonces asigna acciones a entradas:

```ini
InputGas       = key SC_UP
InputShiftUp   = key SC_A
```

**Most Wanted, Carbon, ProStreet y Undercover** se pueden remapear con XtendedInput, que escribe texto plano en `scripts/XtendedInputMaps/<perfil>/NFS_XtendedInput.usermap.ini`:

```ini
FRONTENDACTION_ACCEPT = XINPUT_GAMEPAD_A
GAMEACTION_GAS        = XINPUT_GAMEPAD_RT
```

Las acciones de menú y las de conducción están separadas, lo cual viene bien. La pega es que XtendedInput solo habla XInput y apaga DirectInput, así que esta ruta es para mandos. Los volantes lo necesitan desactivado.

**Underground, Underground 2 y NFS III** guardan sus asignaciones dentro de archivos de guardado binarios. No hay archivo de texto que editar ni forma segura de escribirlos desde fuera, así que esos se mapean dentro del juego y se dejan en paz.

Por eso la herramienta trabaja sobre el dispositivo en vez de sobre los archivos del juego. Moldear lo que recibe el juego es el único enfoque que funciona igual en todas partes.

## Si algo se rompe

**El juego te pide insertar un disco**

No hay unidad óptica en el prefijo. Algunos de estos juegos todavía buscan una y se niegan a arrancar cuando no encuentran nada, incluso con el parche de no-CD puesto.

El script de instalación mapea una unidad `D:` apuntando a la carpeta del juego y la marca como CD-ROM. Si montas un prefijo a mano:

```bash
ln -sfn "$PFX/drive_c/Games/NFSU2" "$PFX/dosdevices/d:"
WINEPREFIX="$PFX" proton run reg.exe add 'HKLM\Software\Wine\Drives' \
    /v 'd:' /t REG_SZ /d cdrom /f
```

Este costó una tarde entera porque solo apareció en la segunda máquina. Un prefijo creado con un pendrive montado hereda letras de unidad por accidente, así que el juego encuentra una unidad y nunca se queja. Crea el mismo prefijo en una máquina limpia y te quedan solo `c:` y `z:`, y aparece la petición del disco. Mismo juego, mismos archivos, mismo registro, resultado distinto. Si algo funciona en una máquina y no en otra, compara `dosdevices` antes que cualquier otra cosa.

**Todos los accesos directos muestran el nombre y el icono del mismo juego**

No pongas `StartupWMClass=steam_proton` en los archivos de acceso directo. Todo juego de Proton abre una ventana con esa clase, así que el escritorio elige el primer acceso que la reclama, por orden alfabético, y etiqueta todos tus juegos con ese. Deja la clave fuera y cada ventana conserva su propia identidad.

**El instalador se detiene justo después de la comprobación de Proton y no imprime nada**

Dos líneas de detección de hardware bajo `set -euo pipefail` hacen eso. Contar mandos con `ls /dev/input/js* | wc -l` falla cuando no hay ninguno conectado, y `pipefail` convierte eso en una salida del script. Lo mismo con un `[[ prueba ]] && echo` suelto, que devuelve 1 cuando la prueba es falsa. Ninguno imprime nada, así que parece que el script terminó.

Recorre el glob en vez de canalizar `ls`, y dale un `else` a toda prueba suelta.

**Resolución equivocada cuando ejecutas el script por SSH**

`xrandr` y `wlr-randr` necesitan un servidor gráfico. Por SSH no hay ninguno, y un script que cae en un valor por defecto fijo escribirá alegremente 1080p en todos los archivos de configuración.

Lee el conector directamente del kernel, que funciona sin sesión alguna:

```bash
for m in /sys/class/drm/*/modes; do
    [ "$(cat "${m%/modes}/status")" = connected ] && head -1 "$m"
done
```

**Un script de prueba que interrumpiste deja un juego roto**

Si un script que mueve archivos muere a medias, puede dejar el juego en un estado que no vas a reconocer después. Uno que había apartado los plugins `.asi` siguió vivo cuarenta minutos, así que faltaba el parche de no-CD y el juego exigía un disco, mientras la carpeta se veía normal cuando alguien fue a mirar.

Antes de depurar nada, ejecuta `ps -eo pid,etime,args | grep -i '\.exe'` y mata lo que sea más viejo que tu sesión. Busca también un `explorer.exe /desktop` perdido, ya que un escritorio de Wine olvidado es un rectángulo negro sobre tu pantalla.

**Un glob no encontró un archivo que está claramente ahí**

Los globs del shell distinguen mayúsculas de minúsculas. `ls *.exe` no coincide con `SPEED2.EXE`. Usa `find . -iname '*.exe'` cuando no controlas las mayúsculas, que con estos juegos es siempre.

**El juego abre pero parece que faltan los mods**

Tu override de `dinput8` no se está aplicando. Mira arriba.

**La ventana del juego sale negra en la captura pero se ve bien en pantalla**

Eso es un problema de la captura, no del juego. `import -window <id>` no puede leer una superficie Vulkan y devuelve una imagen negra. Captura la pantalla entera y recorta:

```bash
import -window root shot.png
```

**Moví la carpeta del juego y el desinstalador se rompió**

Los instaladores Inno Setup escriben la ruta de instalación en el registro. Si mueves la carpeta tienes que actualizar esas claves también.

Lee el registro con el prefijo apagado, si no obtienes resultados viejos. Wine mantiene el registro en memoria y solo escribe `system.reg` y `user.reg` de vez en cuando, así que buscar en esos archivos con el juego o el instalador en marcha puede no mostrarte nada habiendo mucho. Mata `wineserver` primero.

**Un comando `pkill -f` mató tu propia terminal**

`pkill -f` coincide con la línea de comandos completa, incluida la shell que está ejecutando tu script. Usa `pkill -x` con el nombre exacto del proceso.

**Haciéndolo a mano y la instalación silenciosa devuelve 1**

Usa `/VERYSILENT`, no `/SILENT`. Esta es la línea completa que funciona:

```bash
proton run Setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART "/DIR=C:\\Games\\NFSMW"
```

`/SILENT` todavía dibuja una ventana de progreso y no sobrevivió a ser lanzado desde un script aquí. `/VERYSILENT` no dibuja nada y sale con 0. Añade `/LOG=C:\inno.log` si quieres ver qué hizo, el log cae dentro del prefijo y lista cada archivo.

**Cada juego tiene un nombre de ejecutable distinto**

`speed.exe`, `SPEED2.EXE`, `Speed.exe`, y así, con mayúsculas distintas además. El script busca el `.exe` más grande de la carpeta del juego en vez de mantener una lista, que es por lo que funciona en juegos que nadie ha probado todavía. Vale saberlo si escribes tu propio lanzador.

## Dónde va todo

```
~/Games/
├── nfs-most-wanted/           prefijo, juego en pfx/drive_c/Games/NFSMW
├── nfs-underground-2/         prefijo, juego en pfx/drive_c/Games/NFSU2
├── nfs-most-wanted-play.sh    lanzador
├── nfs-underground-2-play.sh  lanzador
└── _installers/nfs/           archivos extraídos
```

`_installers/nfs` guarda los archivos extraídos para que una reinstalación no tenga que leer tu pendrive otra vez. Se acumula rápido, unos 8 GB para cuatro juegos. Bórralo cuando quieras, nada depende de él una vez instalados los juegos:

```bash
rm -rf ~/Games/_installers/nfs
```

Un prefijo por juego a propósito. Son juegos viejos con mods que se enganchan a DLLs del sistema, y mantenerlos separados garantiza que un mod roto en uno no tumbe a otro.

Para quitar un juego, borra su carpeta de prefijo, su lanzador y los dos archivos `.desktop`.

## Créditos

**[MagiPack](https://www.magipack.games/)** armó los repacks, con los parches oficiales y los mods ya conectados. La mayor parte del trabajo aquí ya estaba hecha por ellos.

**[ThirteenAG](https://github.com/ThirteenAG/WidescreenFixesPack)** escribió los parches de pantalla ancha y el Ultimate ASI Loader que hacen jugables estos juegos en pantallas modernas.

**[Evgeny Vrublevsky](http://veg.by/en/projects/nfs3/)** por el Modern Patch de NFS III.

**[GloriousEggroll](https://github.com/GloriousEggroll/proton-ge-custom)** por GE-Proton.

**Bladez1992 y Legacy Gamers' Union** por el repack de Hot Pursuit 2, y **[xan1242](https://github.com/xan1242/hp2wsfix)** por hp2wsfix.

Yo solo resolví la parte de Linux y la escribí.

## Contribuyendo

¿Hiciste funcionar alguno de los juegos sin probar? ¿O Hot Pursuit 2? Abre un issue con tu distro, tu GPU y lo que cambiaste. Los reportes desde Bazzite y Steam Deck son especialmente bienvenidos.

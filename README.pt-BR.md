# OpenForSpeed

**Jogue os Need for Speed clássicos no Linux.** Oito deles, com as correções de widescreen e os mods gráficos já configurados, controle e volante funcionando, um script só e sem sudo.

> Underground · Underground 2 · Most Wanted · Carbon · ProStreet · Undercover · NFS III Hot Pursuit · Hot Pursuit 2

**Leia em outros idiomas:** [English](README.md) · [Español](README.es.md)

Testado em sistemas baseados em Ubuntu e em Fedora, e feito para funcionar também no **Bazzite, SteamOS e Steam Deck**, onde você não consegue instalar nada no sistema. Tudo fica dentro da sua pasta pessoal.

Esses jogos saíram entre 1998 e 2008. Nenhum deles é vendido hoje. A comunidade mantém eles vivos com repacks e mods, e eles rodam muito bem no Linux depois que você descobre as duas ou três configurações que importam. Este repositório é essas configurações mais um script que faz a parte chata.

Se isso te ajudar a rodar algum deles, uma estrela facilita a vida da próxima pessoa que procurar.

![Hot Pursuit 2 rodando no Linux em 3440x1440](screenshots/hot-pursuit-2.png)

## O que funciona

| Jogo | Ano | Status | Observações |
|---|---|---|---|
| Need for Speed Underground | 2003 | joga | widescreen, opções extras |
| Need for Speed Underground 2 | 2004 | joga | widescreen, opções extras |
| Need for Speed Most Wanted | 2005 | joga | widescreen, reflexos em HD, HUD adaptado, áudio DSOAL |
| Need for Speed Carbon | 2006 | joga | widescreen, reflexos em HD, HUD adaptado, EA Trax nas corridas |
| Need for Speed ProStreet | 2007 | joga | use o repack ElAmigos, não o MagiPack |
| Need for Speed Undercover | 2008 | joga | coloque o modo de janela em 4 e escolha a resolução dentro do jogo |
| Need for Speed III Hot Pursuit | 1998 | joga | só teclado, o controle precisa de um mapeador |
| Need for Speed Hot Pursuit 2 | 2002 | joga | force o d3d8 embutido, explicado abaixo |

Joga quer dizer que alguém correu uma prova inteira com controle. Roda quer dizer que abre e desenha na tela, mas ainda não teve uma sessão completa. Se você for mais longe com algum deles, abre uma issue e conta como.

Testado nesta máquina:

| | |
|---|---|
| Sistema | Zorin OS 18.1 (base Ubuntu 24.04) |
| Kernel | 7.0.0-28-generic |
| Ambiente | GNOME no X11, três monitores |
| CPU | AMD Ryzen 9 3900X, 24 threads |
| RAM | 62 GB |
| GPU | NVIDIA RTX 4070 Ti, driver 580.173.02 |
| Vulkan | 1.4.312 |
| Proton | GE-Proton11-3 |
| Controle | Xbox por USB |

Tudo é instalado dentro da sua pasta pessoal. Sem sudo, então funciona também no Bazzite, SteamOS e outros sistemas imutáveis.

## Conseguindo os jogos

Todos vieram do [myabandonware](https://www.myabandonware.com/search/q/need+for+speed/pla/4). Procure o jogo, abra a página dele e pegue exatamente o arquivo listado abaixo. O script acha cada jogo pelo nome do arquivo, então baixe e não renomeie nada.

| Jogo | Arquivo |
|---|---|
| Underground | `Need-for-Speed-Underground_Win_EN_MagiPack.zip` |
| Underground 2 | `Need-for-Speed-Underground-2_Win_EN_MagiPack.zip` |
| Most Wanted | `Need-for-Speed-Most-Wanted_Win_EN_MagiPack.zip` |
| Carbon | `Need-for-Speed-Carbon_Win_EN_MagiPack.zip` |
| ProStreet | `Need-for-Speed-ProStreet_Win_EN-FR-DE-IT-ES-NL-DA-FI-SV-HU-CS-PL-RU_Repack.zip` |
| Undercover | `Need-for-Speed-Undercover_Win_EN-FR-DE-IT-ES-NL-SV-DA-FI-PL-RU-CS-HU_Repack.zip` |
| NFS III Hot Pursuit | `Need-for-Speed-III-Hot-Pursuit_Win_EN-FR-ES-DE-IT_Modern-Bundle.zip` |
| Hot Pursuit 2 | `Need-for-Speed-Hot-Pursuit-2_Win_EN_LGU-Repack-by-Bladez1992.zip` |

São exatamente as versões contra as quais tudo aqui foi testado. Outros lançamentos do mesmo jogo podem funcionar, mas essas são as que eu sei que funcionam.

### O ProStreet é a exceção

Não use o `Need-for-Speed-ProStreet_Win_EN_MagiPack.zip`. Eu tentei ele primeiro, porque as builds MagiPack são a melhor escolha para todos os outros jogos, e ele quebra na abertura toda vez com o mesmo page fault. Os detalhes estão mais abaixo.

O repack ElAmigos da tabela acima abre sem drama. Ele traz o jogo puro, sem mods, e o script baixa a correção de widescreen para ele durante a instalação.

### Baixando

Os arquivos são grandes e os servidores têm tempo de espera. O [JDownloader](https://jdownloader.org/) enfileira tudo e lida com a espera enquanto você faz outra coisa:

```bash
flatpak install flathub org.jdownloader.JDownloader
```

Coloque tudo numa pasta só. O script procura recursivamente, então subpastas não são problema.

## Instalação

```bash
git clone https://github.com/agentkyo/openforspeed.git
cd openforspeed
./install.sh --list
./install.sh --source ~/Downloads --game most-wanted
```

Instalar vários de uma vez:

```bash
./install.sh --source ~/Downloads --game underground --game underground-2 --game most-wanted
```

Ou tudo que ele encontrar:

```bash
./install.sh --source ~/Downloads --all
```

Conferir seu sistema sem instalar nada:

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

A instalação inteira roda sozinha. Os instaladores MagiPack aceitam `/VERYSILENT`, então não tem assistente para clicar. Quando termina você fica com um script de atalho em `~/Games` e ícones na área de trabalho e no menu de aplicativos.

## Ele configura os jogos para o seu hardware

Do jeito que vêm, esses jogos rodam em 800x600 com configurações de 2005. O script olha sua máquina e reescreve os arquivos de configuração dos mods para você ter sua resolução real e gráficos compatíveis com o que sua GPU aguenta.

Ele lê seu monitor principal pelo `xrandr`, o fabricante da GPU pelo `lspci` e a VRAM pelo `nvidia-smi`, pelos arquivos do sysfs da AMD ou pelo `vulkaninfo`, o que responder primeiro. Nenhuma ferramenta extra para instalar, o que importa no Bazzite e no Steam Deck, onde você não pode simplesmente instalar um pacote.

Três presets, escolhidos pela VRAM:

| Preset | VRAM | Resolução das sombras | Escala dos reflexos | Sombras no retrovisor |
|---|---|---|---|---|
| high | 6 GB ou mais | 8192 | 2.0x | ligado |
| medium | 2 a 6 GB | 4096 | 1.5x | desligado |
| low | menos de 2 GB | 1024 | 1.0x | desligado |

Ele também define sua resolução nativa, liga os ícones de botão de controle se achar um conectado, e pula os vídeos de abertura.

Todo comentário nos arquivos ini fica intacto, então você pode abrir e ajustar o que quiser depois. O ThirteenAG documentou cada opção ali dentro do próprio arquivo.

Além dos presets, ele liga tudo que não custa nada e só melhora o jogo: correções de sombra, reflexos mais detalhados, HUD ajustado para ultrawide, taxa de quadros liberada nos jogos que suportam, as proteções contra crash que o ThirteenAG inclui, e o pulo dos vídeos de abertura.

Refaça o ajuste quando quiser, por exemplo depois de trocar de monitor ou de GPU:

```bash
./install.sh --tune-only --all
```

Ou pule ele por completo e mantenha o padrão dos mods:

```bash
./install.sh --source ~/Downloads --all --no-tune
```

### Uma dúvida em aberto

A correção de widescreen tem uma opção `ForcedGPUVendor` que informa ao jogo com qual marca de GPU ele está falando. O script coloca a sua GPU real.

O detalhe é que o DXVK esconde sua GPU real do jogo e reporta um dispositivo AMD por padrão. Então o valor realmente correto no Proton talvez seja `0x1002` independente da placa que você tem. Não consegui testar direito com só uma NVIDIA aqui, e na NVIDIA o padrão do mod já bate, então não muda nada de um jeito ou de outro. Se você tem uma AMD ou Intel e nota diferença, me conta.

## As duas configurações que realmente importam

Se você prefere montar tudo na mão, essa é a versão curta.

**1. Carregue os mods com um override de DLL.**

As correções do ThirteenAG andam em cima do Ultimate ASI Loader, que vem como um `dinput8.dll` falso na pasta do jogo. O Wine carrega o `dinput8` dele a não ser que você mande o contrário, e aí o jogo abre sem widescreen, sem reflexos em HD e sem as correções de controle. Parece que os mods nunca foram instalados.

```bash
WINEDLLOVERRIDES="dinput8=n,b"
```

O Most Wanted também traz o DSOAL para áudio posicional, que se esconde atrás do `dsound.dll`:

```bash
WINEDLLOVERRIDES="dinput8=n,b;dsound=n,b"
```

**2. Use GE-Proton, não Wine puro.**

O DXVK converte as chamadas do DirectX 9 para Vulkan e esses jogos voam. O GE-Proton11-3 traz o DXVK 3.0.2 e é essa combinação que foi testada aqui.

Uma coisa para saber: [o DXVK 2.5.2 e o 2.5.3 quebram o Most Wanted](https://github.com/doitsujin/dxvk/issues/4624) com uma violação de acesso na abertura. Se você está num Proton mais antigo e o jogo morre antes do menu, provavelmente é isso. O 3.0.2 está bom.

Confirme que os mods carregaram em vez de supor:

```bash
pgrep -x speed.exe | while read p; do tr '\0' '\n' < /proc/$p/maps; done | grep -oiE "[^/]*\.asi" | sort -u
```

Você deve ver os arquivos `.asi` listados. Se voltar vazio, seu override não foi aplicado.

## Controle

O Undercover veio com o melhor tratamento de controle do grupo, então o script dá essa mesma configuração para os outros.

Ela vem do [NFS-XtendedInput](https://github.com/xan1242/NFS-XtendedInput) do xan1242, que troca o código de entrada antigo por XInput de verdade. Você ganha ícones de botão corretos, analógicos e gatilhos funcionando, e o jogo pausa quando você desconecta o controle, igual console. O script baixa e instala para Most Wanted, Carbon, ProStreet e Undercover, e depois aplica as mesmas zonas mortas em todos:

```ini
PercentLS = 0.24                    analógico esquerdo
PercentRS = 0.24                    analógico direito
Percent_Shifting = 0.75             o quanto o gatilho anda antes de contar
Percent_AnalogStickDigital = 0.50   analógico como direcional
PassConnStatus = 1                  pausa quando o controle cai
```

Underground e Underground 2 não têm build do XtendedInput, então usam o `ImproveGamepadSupport` do ThirteenAG, que o script também liga. Funciona bem, só tem menos ajustes.

### Controle ou volante, você tem que escolher

O XtendedInput fala isso com todas as letras no readme dele: **"Currently KILLS Direct Input, beware"**. O DirectInput é por onde os volantes aparecem, então com o XtendedInput instalado seu volante some desses quatro jogos.

Então existem dois modos:

```bash
./install.sh --source ~/Downloads --all                  # controle, o padrão
./install.sh --source ~/Downloads --all --input wheel    # volante
```

Trocar depois, sem reinstalar nada:

```bash
./install.sh --tune-only --all --input wheel
./install.sh --tune-only --all --input gamepad
```

Ele só renomeia o arquivo `.asi`, então ir e voltar leva um segundo.

Underground, Underground 2, NFS III e Hot Pursuit 2 não são afetados de nenhum jeito. Eles nunca recebem o XtendedInput, então o volante funciona nos quatro independente do modo escolhido.

Mais uma coisa sobre o Most Wanted: com o XtendedInput ligado, o menu de Controles dentro do jogo fica desativado porque ele quebra o jogo. É o mod fazendo isso de propósito. Use o modo volante se você precisa desse menu.

Uma observação para quem for instalar na mão: o XtendedInput e a correção do ThirteenAG trazem os dois um `dinput8.dll`, e se você deixar um sobrescrever o outro fica com um jogo que não abre. Os dois são o mesmo carregador de ASI, e ele carrega todo `.asi` da pasta `scripts/`, então mantenha um `dinput8.dll` só e coloque os dois `.asi` lado a lado. É o que o script faz.

**Feche a Steam antes de jogar.** O Steam Input pega controle exclusivo do gamepad. O jogo continua listando o controle mas nunca recebe um botão, então parece quebrado sem estar. Os atalhos avisam se a Steam estiver aberta. Se você quer manter a Steam aberta mesmo assim, desligue o suporte a controle Xbox em Configurações, Controle.

### Volantes funcionam melhor que controles nos jogos antigos

Se você tem um volante, use. Um Logitech G29 aparece no DirectInput, que é exatamente onde os dois jogos antigos procuram e exatamente onde um controle de Xbox nunca aparece:

```
Connected (DirectInput devices)
  Logitech G29 Driving Force Racing Wheel

Connected (XInput devices)
  Controller (Xbox One For Windows)
```

O problema inteiro está nessa tela. NFS III e Hot Pursuit 2 são de 1998 e 2002, época em que um volante DirectInput era o jeito normal de jogar corrida, então eles enxergam o volante numa boa enquanto o controle moderno é invisível para eles.

Nada para instalar do lado do Wine. Se o kernel enxerga o volante, o jogo também enxerga. Confira com:

```bash
ls /dev/input/by-id/ | grep -i wheel
lsmod | grep -E "hid_logitech|ff_memless"
```

O `ff_memless` carregado quer dizer que o force feedback está disponível.

### Combine os pedais ou os jogos enlouquecem

Um G29 reporta acelerador, freio e embreagem como três eixos separados que ficam no valor máximo quando você não está pisando neles. Jogos dessa época esperam um eixo de pedal só, centrado no zero, então eles leem esse valor de repouso como entrada máxima. O resultado é o Hot Pursuit 2 acelerando sozinho antes de você tocar em qualquer coisa, e o ProStreet rolando o menu para baixo sem parar até você pisar na embreagem e sem querer devolver o eixo para o meio.

A correção é uma configuração só:

```bash
flatpak install flathub io.github.berarma.Oversteer
flatpak run io.github.berarma.Oversteer --combine-pedals 1 --range 270
```

O Oversteer não consegue mexer no volante até você dar permissão, e ele não instala a regra do udev sozinho:

```bash
sudo curl -o /etc/udev/rules.d/99-logitech-wheel-perms.rules \
  https://raw.githubusercontent.com/berarma/oversteer/master/data/udev/99-logitech-wheel-perms.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Desconecte o volante e conecte de novo. Esse é o único comando deste guia inteiro que precisa de sudo.

### Um perfil por jogo

O script escreve um perfil do Oversteer para cada jogo e os atalhos carregam ele antes do jogo abrir, então o volante fica certo sem você pensar nisso. A rotação é mais fechada nos jogos arcade e mais aberta no ProStreet, e o force feedback é mais forte nos antigos, onde os efeitos são mais grosseiros.

| Jogo | Rotação |
|---|---|
| NFS III, Hot Pursuit 2 | 270 |
| Underground, Underground 2, Most Wanted, Carbon | 270 |
| Undercover | 300 |
| ProStreet | 360 |

Todos usam `combine_pedals = 1`. Edite qualquer um deles no Oversteer e suas mudanças ficam, os atalhos só carregam o que o perfil disser.

Os perfis também levam valores de autocentro, ganho, mola e amortecimento, mas confira se o seu volante aceita eles antes de gastar tempo ajustando. Num G29 com o driver padrão do kernel, só existem três arquivos:

```bash
ls /sys/bus/hid/devices/*046D*/ | grep -E "range|combine|alternate"
```

São `range`, `combine_pedals` e `alternate_modes`. As configurações de intensidade do force feedback precisam do [new-lg4ff](https://github.com/berarma/new-lg4ff), que substitui o driver padrão. Sem ele, esses valores são escritos no perfil, o Oversteer aceita, e nada acontece. O force feedback em si continua funcionando, você só não consegue ajustar a força por aqui.

Instale o new-lg4ff se quiser esse controle. As duas configurações que resolvem os problemas de verdade, combinar os pedais e fechar a rotação, funcionam bem no driver padrão.

### Os dois antigos

NFS III e Hot Pursuit 2 são de 1998 e 2002 e só falam o DirectInput antigo. O Wine entrega os controles modernos para o XInput, então esses dois ou não enxergam nada ou enxergam algo para o qual não têm perfil.

O Hot Pursuit 2 enxerga o controle. Ele diz que não reconhece e te manda para Controller Options, onde você mapeia os botões na mão. Faça isso e funciona durante as corridas, mas os menus continuam só no teclado. Um volante não tem esse problema.

O NFS III não enxerga nada. Mapeie o controle para o teclado:

```bash
flatpak install flathub io.github.antimicrox.antimicrox
```

Amarre os analógicos e gatilhos nas setas, deixe rodando, e jogue. O menu Controllers do próprio jogo mostra qual tecla faz o quê.

Não tente desligar o SDL no `winebus` para forçar DirectInput. Eu testei e piora. Controles de Xbox usam o driver `xpad` do kernel, que entrega nós evdev e nenhum nó hidraw, então com o SDL desligado o Wine perde o controle completamente.

## Notas por jogo

**Most Wanted** traz o DSOAL para áudio melhor. Tem presets em `~DSOAL` dentro da pasta do jogo se você quiser mexer.

**Underground 2** teve a trilha sonora restaurada no repack v4. Se você quiser a original censurada, apague `pfdata` e `speech` na pasta do jogo e renomeie `SDATA.Backup` para `SDATA`.

**Undercover** inclui o NFS VltEd na pasta do jogo, caso você queira entrar no mundo de modificar os arquivos.

**Undercover** abre numa janelinha porque o repack vem com `WindowedMode = 1`. Coloque `4` em `scripts/NFSUndercover.GenericFix.ini` para tela cheia sem borda, o que o script já faz para você. Depois disso, abra as opções de vídeo dentro do jogo e escolha sua resolução. O jogo abre em 1920x1080 e num setup de vários monitores ele vai parar naquele que bate, não necessariamente no principal.

**ProStreet** funciona, mas só com o repack ElAmigos. O MagiPack quebra na abertura toda vez, sempre no mesmo endereço:

```
Unhandled page fault on write access to 0x00007077 at address 0x01F6880E, wow64 32-bit code
```

Coisas que não mudaram nada:

- GE-Proton11-3 com DXVK
- GE-Proton11-3 com DXVK desligado (`PROTON_USE_WINED3D=1`)
- wine-staging 11.14 puro
- Remover todos os mods renomeando o `dinput8.dll`
- Adicionar o override `d3dx9_34=n,b` que recomendam para esse jogo

Mesmo crash, mesmo endereço, toda vez, inclusive sem mod nenhum. Então é o executável do jogo, não o Wine e não a pilha de mods.

Outras pessoas rodam o ProStreet no Linux, mas com uma build diferente. A [thread do r/linux_gaming](https://www.reddit.com/r/linux_gaming/) que trata disso usa uma versão cujo executável é `nfs.exe`, enquanto esse repack traz `nfsps.exe`. Os comentários de lá apontam para a necessidade de um executável corrigido para o Wine, que o [Pepega Mod](https://pepegamod.com/pepega-download/) inclui. Se você fizer outra build funcionar, abre uma issue e diz qual.

**NFS III** não é uma instalação normal. É o [Modern Bundle do Evgeny Vrublevsky](http://veg.by/en/projects/nfs3/), que é uma versão reescrita com widescreen, suporte a múltiplos núcleos e sem uso de registro. O script só extrai e ajusta o `nfs3.ini` para você.

O jogo roda muito bem, mas não enxerga seu controle. Ele é de 1998 e só fala DirectInput, enquanto o Wine entrega os controles modernos para o XInput. Abra `control joy.cpl` no prefixo e você vê por conta própria: o controle está em "XInput devices" e a lista "DirectInput devices" está vazia.

Desligar o SDL no `winebus` não resolve, piora. Controles de Xbox usam o driver `xpad`, que cria nós evdev e nenhum hidraw, então com o SDL desligado o Wine perde o controle completamente e as duas listas ficam vazias. Testado, não perca tempo.

O que funciona é mapear o controle para o teclado, que é a resposta de sempre para jogos anteriores a 2000:

```bash
flatpak install flathub io.github.antimicrox.antimicrox
```

Abra o AntiMicroX, escolha seu controle, e amarre os analógicos e gatilhos nas setas mais o que mais quiser. O NFS III tem suporte completo a teclado e o menu Controllers dele mostra as teclas atuais. Deixe o AntiMicroX rodando enquanto joga.

**Hot Pursuit 2** funciona, e o aviso sobre DirectPlay no readme dele acabou sendo pista falsa. O Wine traz o próprio `dplay.dll` e `dplayx.dll`, e se você rastrear o jogo rodando dá para ver que o DirectPlay nunca é sequer carregado. Ele só é necessário para jogar em rede local.

Duas coisas são específicas dele:

É um jogo DirectX 8 e o repack traz o próprio wrapper `d3d8.dll`, que traduz D3D8 para D3D9. Deixe esse wrapper rodar e o cenário aparece certo, mas todo carro sai sem textura, azul e vermelho chapados, com um bloco magenta na tela de escolha de carro. Magenta é a cor clássica de textura faltando, e é exatamente isso que é.

Diga ao Wine para usar o d3d8 dele e os carros voltam com textura:

```
WINEDLLOVERRIDES="d3d8=b;dinput8=n,b"
```

Repare no `b` sozinho, não `n,b`. Isso quer dizer só o embutido, então o arquivo do wrapper pode ficar onde está e o Wine simplesmente ignora. Isso te joga no wined3d em vez do DXVK, o que para um jogo de 2002 não é problema.

Fazer isso também desativa o HP2WSFix, já que era aquele wrapper que carregava ele. O jogo continua rodando na resolução que você definir e a imagem não fica esticada, então você não perde muito.

A resolução dele não está no menu do jogo. Edite este arquivo e ajuste tanto `[Graphics]` quanto `[GraphicsFE]`:

```
~/Games/nfs-hot-pursuit-2/pfx/drive_c/users/steamuser/Documents/EA Games/Need For Speed Hot Pursuit 2/rendercaps.ini
```

```ini
Width=3440
Height=1440
```

Sobre o controle: o jogo mostra "Your controller is not specifically recognized" e te manda para Controller Options. Ele enxerga o controle, só não tem perfil para um Xbox porque o jogo é anterior a ele. Mapeie os botões na mão em Controller Options, ou use o AntiMicroX como no NFS III.

## A ferramenta de entrada

Tudo acima configura o volante pelo driver, e isso só vai até certo ponto. Alguns desses jogos leem os valores brutos dos eixos e ignoram a zona morta que o kernel informa, então um pedal de embreagem que descansa no valor máximo é lido como uma direção de menu pressionada, não importa o que você configure. Trocar o volante para um modo de compatibilidade mais antigo até silencia esse pedal, mas aí o volante aparece como outro dispositivo e todos os mapeamentos que você salvou no jogo param de funcionar.

O `tools/ofs_input.py` segue outro caminho. Ele lê o volante ou o controle real, aplica suas configurações, e publica um segundo dispositivo virtual construído do zero. O jogo só enxerga esse.

```bash
python3 tools/ofs_input.py list
python3 tools/ofs_input.py monitor
python3 tools/ofs_input.py calibrate --profile wheel
python3 tools/ofs_input.py bridge --profile wheel
```

O `list` mostra cada dispositivo com seus eixos e marca os que descansam fora do centro, que é o que causa menu rolando sozinho. O `monitor` desenha barras ao vivo para você ver o que cada pedal faz de verdade. O `calibrate` te guia por cada eixo: manter ou descartar, inverter, definir zona morta. O `bridge` então roda o dispositivo virtual.

O que isso te dá:

- **O force feedback continua funcionando.** A ponte declara os mesmos efeitos que o volante real suporta e repassa eles, traduzindo os identificadores de efeito nos dois sentidos. Sem isso o jogo mostra o force feedback como indisponível, já que um dispositivo virtual que só envia eixos e botões não consegue receber efeitos.
- **Intensidade do force feedback ajustável.** O driver padrão `hid-logitech` não tem controle de ganho, então o Oversteer não consegue mudar. A ponte escala a magnitude do efeito na passagem, o que funciona em qualquer driver. Defina durante a calibração, 100 mantém o que o jogo pedir.
- **Descartar um eixo por completo.** A embreagem nunca chega ao jogo, então não tem como segurar uma direção de menu.
- **Zonas mortas que funcionam.** Elas são aplicadas antes do evento ser enviado, então o jogo recebe um valor já limpo em vez de ter que respeitar uma dica.
- **Inversão por eixo**, para pedais ligados ao contrário.
- **Uma identidade de dispositivo estável.** O dispositivo virtual sempre tem o mesmo nome, então seus mapeamentos no jogo sobrevivem a desconectar e reconectar, trocar de modo e alternar entre PS3 e PS4. Essa é a parte que mais importa. Mudar o modo do volante para resolver a embreagem custou um remapeamento inteiro uma vez.

Não precisa de root nem de pacotes. O `/dev/uinput` já é gravável pelo seu usuário na maioria dos desktops, e tudo é biblioteca padrão, o que também quer dizer que funciona no Bazzite e no SteamOS, onde você não consegue instalar pacotes Python no sistema.

Faixa de rotação, force feedback e pedais combinados continuam sendo do Oversteer. Os dois trabalham juntos: o Oversteer prepara o hardware, essa ferramenta molda o que o jogo lê.

### Escolhendo seu dispositivo quando um jogo abre

Os atalhos abrem um menu antes do jogo:

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

Cada opção te diz se existe um perfil e o que tem dentro dele, então você sabe com o que vai jogar. Se algum eixo descansa fora do centro, ele avisa ali mesmo, porque é isso que faz menu rolar sozinho.

A contagem regressiva só roda quando você já escolheu algo para aquele jogo antes. Qualquer tecla para ela. Escolha uma opção que ainda não tem perfil e ele calibra primeiro, em vez de abrir algo meio configurado.

Volante e controle mantêm perfis separados, então você pode configurar os dois e alternar por jogo. O `c` calibra qualquer um, o `d` apaga qualquer um, o `f` limpa a escolha salva para aquele jogo.

## Como cada jogo guarda seus mapeamentos

Vale saber antes de gastar uma noite tentando editar o arquivo errado.

**Hot Pursuit 2** é o único totalmente aberto. O `Controllers/definitions.ini` descreve cada dispositivo, inclusive onde cada eixo descansa:

```ini
axis0 = 0,left,127,0,kTxtAxis0Left
```

Isso é o eixo 0, direção esquerda, descansando em 127, extremo em 0. Acertar esse valor de repouso é exatamente o que impede um pedal de ser lido como pressionado. O `Controllers/defaults.ini` então liga as ações às entradas:

```ini
InputGas       = key SC_UP
InputShiftUp   = key SC_A
```

**Most Wanted, Carbon, ProStreet e Undercover** podem ser remapeados pelo XtendedInput, que grava texto puro em `scripts/XtendedInputMaps/<perfil>/NFS_XtendedInput.usermap.ini`:

```ini
FRONTENDACTION_ACCEPT = XINPUT_GAMEPAD_A
GAMEACTION_GAS        = XINPUT_GAMEPAD_RT
```

Ações de menu e ações de direção são separadas, o que ajuda. O problema é que o XtendedInput só fala XInput e desliga o DirectInput, então esse caminho é para controle. Volantes precisam dele desativado.

**Underground, Underground 2 e NFS III** guardam os mapeamentos dentro de arquivos de save binários. Não tem arquivo de texto para editar e nem jeito seguro de escrever por fora, então esses são mapeados dentro do jogo e deixados em paz.

É por isso que a ferramenta trabalha no dispositivo em vez de nos arquivos do jogo. Moldar o que o jogo recebe é a única abordagem que funciona igual em todo lugar.

## Se algo quebrar

**O jogo pede para inserir um disco**

Não existe unidade óptica no prefixo. Alguns desses jogos ainda procuram uma e se recusam a abrir quando não acham nada, mesmo com a correção de no-CD no lugar.

O script de instalação mapeia um drive `D:` apontando para a pasta do jogo e marca ele como CD-ROM. Se você montar um prefixo na mão:

```bash
ln -sfn "$PFX/drive_c/Games/NFSU2" "$PFX/dosdevices/d:"
WINEPREFIX="$PFX" proton run reg.exe add 'HKLM\Software\Wine\Drives' \
    /v 'd:' /t REG_SZ /d cdrom /f
```

Esse custou uma noite inteira porque só apareceu na segunda máquina. Um prefixo criado com um pendrive montado herda letras de drive por acidente, então o jogo acha uma unidade e nunca reclama. Crie o mesmo prefixo numa máquina limpa e você tem só `c:` e `z:`, e o pedido de disco aparece. Mesmo jogo, mesmos arquivos, mesmo registro, resultado diferente. Se algo funciona numa máquina e não em outra, compare o `dosdevices` antes de comparar qualquer outra coisa.

**Todos os atalhos mostram o nome e o ícone do mesmo jogo**

Não coloque `StartupWMClass=steam_proton` nos arquivos de atalho. Todo jogo do Proton abre uma janela com essa classe, então o sistema escolhe o primeiro atalho que reivindica ela, em ordem alfabética, e rotula todos os seus jogos com aquele. Deixe a chave de fora e cada janela mantém a própria identidade.

**O instalador para logo depois da checagem do Proton e não imprime nada**

Duas linhas de detecção de hardware sob `set -euo pipefail` fazem isso. Contar controles com `ls /dev/input/js* | wc -l` falha quando nenhum está conectado, e o `pipefail` transforma isso numa saída do script. O mesmo vale para um `[[ teste ]] && echo` solto, que retorna 1 quando o teste é falso. Nenhum dos dois imprime nada, então parece que o script terminou.

Percorra o glob em vez de canalizar o `ls`, e dê um `else` para todo teste solto.

**Resolução errada quando você roda o script por SSH**

O `xrandr` e o `wlr-randr` precisam de um servidor gráfico. Por SSH não existe nenhum, e um script que cai num padrão fixo vai alegremente escrever 1080p em todos os arquivos de configuração.

Leia o conector direto do kernel, o que funciona sem sessão nenhuma:

```bash
for m in /sys/class/drm/*/modes; do
    [ "$(cat "${m%/modes}/status")" = connected ] && head -1 "$m"
done
```

**Um script de teste que você interrompeu deixa um jogo quebrado**

Se um script que move arquivos morre no meio, ele pode deixar o jogo num estado que você não vai reconhecer depois. Um que tinha movido os plugins `.asi` para o lado ficou vivo por quarenta minutos, então a correção de no-CD estava faltando e o jogo exigia um disco, enquanto a pasta parecia normal quando alguém foi olhar.

Antes de depurar qualquer coisa, rode `ps -eo pid,etime,args | grep -i '\.exe'` e mate o que for mais velho que sua sessão. Procure também um `explorer.exe /desktop` perdido, já que uma área de trabalho do Wine esquecida é um retângulo preto por cima da sua tela.

**Um glob não achou um arquivo que está claramente ali**

Globs do shell diferenciam maiúsculas de minúsculas. `ls *.exe` não casa com `SPEED2.EXE`. Use `find . -iname '*.exe'` quando você não controla a capitalização, o que com esses jogos é sempre.

**O jogo abre mas parece que os mods não estão lá**

Seu override do `dinput8` não foi aplicado. Veja acima.

**A janela do jogo aparece preta na captura de tela mas está normal na tela**

Isso é problema da captura, não do jogo. O `import -window <id>` não consegue ler uma superfície Vulkan e devolve uma imagem preta. Capture a tela inteira e recorte:

```bash
import -window root shot.png
```

**Movi a pasta do jogo e o desinstalador quebrou**

Os instaladores Inno Setup gravam o caminho de instalação no registro. Se você mover a pasta, precisa atualizar essas chaves também.

Leia o registro com o prefixo desligado, senão você recebe resultados velhos. O Wine mantém o registro em memória e só escreve o `system.reg` e o `user.reg` de vez em quando, então procurar nesses arquivos com o jogo ou o instalador rodando pode não mostrar nada mesmo tendo bastante coisa. Mate o `wineserver` antes.

**Um comando `pkill -f` matou o seu próprio terminal**

O `pkill -f` casa com a linha de comando inteira, incluindo o shell que está rodando seu script. Use `pkill -x` com o nome exato do processo.

**Fazendo na mão e a instalação silenciosa retorna 1**

Use `/VERYSILENT`, não `/SILENT`. Essa é a linha completa que funciona:

```bash
proton run Setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART "/DIR=C:\\Games\\NFSMW"
```

O `/SILENT` ainda desenha uma janela de progresso e não sobreviveu a ser iniciado por um script aqui. O `/VERYSILENT` não desenha nada e sai com 0. Adicione `/LOG=C:\inno.log` se quiser ver o que ele fez, o log cai dentro do prefixo e lista cada arquivo.

**Cada jogo tem um nome de executável diferente**

`speed.exe`, `SPEED2.EXE`, `Speed.exe`, e por aí vai, com capitalizações diferentes também. O script acha o maior `.exe` da pasta do jogo em vez de manter uma lista, que é por isso que funciona em jogos que ninguém testou ainda. Vale saber se você for escrever seu próprio atalho.

## Onde tudo fica

```
~/Games/
├── nfs-most-wanted/           prefixo, jogo em pfx/drive_c/Games/NFSMW
├── nfs-underground-2/         prefixo, jogo em pfx/drive_c/Games/NFSU2
├── nfs-most-wanted-play.sh    atalho
├── nfs-underground-2-play.sh  atalho
└── _installers/nfs/           arquivos extraídos
```

O `_installers/nfs` guarda os arquivos extraídos para que uma reinstalação não precise ler seu pendrive de novo. Isso acumula rápido, uns 8 GB para quatro jogos. Apague quando quiser, nada depende disso depois que os jogos estão instalados:

```bash
rm -rf ~/Games/_installers/nfs
```

Um prefixo por jogo de propósito. São jogos antigos com mods que se enganham em DLLs do sistema, e manter eles separados garante que um mod quebrado num não derrube outro.

Para remover um jogo, apague a pasta do prefixo, o atalho e os dois arquivos `.desktop`.

## Créditos

**[MagiPack](https://www.magipack.games/)** montou os repacks, com os patches oficiais e os mods já conectados. A maior parte do trabalho aqui já tinha sido feita por eles.

**[ThirteenAG](https://github.com/ThirteenAG/WidescreenFixesPack)** escreveu as correções de widescreen e o Ultimate ASI Loader que tornam esses jogos jogáveis em telas modernas.

**[Evgeny Vrublevsky](http://veg.by/en/projects/nfs3/)** pelo Modern Patch do NFS III.

**[GloriousEggroll](https://github.com/GloriousEggroll/proton-ge-custom)** pelo GE-Proton.

**Bladez1992 e Legacy Gamers' Union** pelo repack do Hot Pursuit 2, e **[xan1242](https://github.com/xan1242/hp2wsfix)** pelo hp2wsfix.

Eu só descobri o lado Linux e escrevi tudo.

## Contribuindo

Conseguiu rodar algum dos jogos não testados? Ou o Hot Pursuit 2? Abre uma issue com sua distro, sua GPU e o que você mudou. Relatos de Bazzite e Steam Deck são especialmente bem-vindos.

# Yet Another (Super) Chip 8 Emulator

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/craigthomas/Chip8Python/python-app.yml?style=flat-square&branch=main)](https://github.com/craigthomas/Chip8Python/actions)
[![Codecov](https://img.shields.io/codecov/c/gh/craigthomas/Chip8Python?style=flat-square)](https://codecov.io/gh/craigthomas/Chip8Python) 
[![Dependencies](https://img.shields.io/librariesio/github/craigthomas/Chip8Python?style=flat-square)](https://libraries.io/github/craigthomas/Chip8Python)
[![Releases](https://img.shields.io/github/release/craigthomas/Chip8Python?style=flat-square)](https://github.com/craigthomas/Chip8Python/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)

An Octo compatible XO Chip, Super Chip, and Chip 8 emulator.

## Table of Contents

1. [What is it?](#what-is-it)
2. [License](#license)
3. [Installing](#installing)
   1. [Ubuntu Installation](#ubuntu-installation)
   2. [Windows Installation](#windows-installation)
4. [Running](#running)
   1. [Running a ROM](#running-a-rom)
   2. [Screen Scale](#screen-scale)
   3. [Instructions Per Second](#instructions-per-second)
   4. [Quirks Modes](#quirks-modes)
      1. [Shift Quirks](#shift-quirks) 
      2. [Index Quirks](#index-quirks)
      3. [Jump Quirks](#jump-quirks)
      4. [Clip Quirks](#clip-quirks)
      5. [Logic Quirks](#logic-quirks)
   5. [Memory Size](#memory-size)
   6. [Colors](#colors)
5. [Customization](#customization)
   1. [Keys](#keys)
   2. [Debug Keys](#debug-keys)
6. [ROM Compatibility](#rom-compatibility)
7. [Further Documentation](#further-documentation)

## What is it?

This project is a Chip 8 emulator written in Python 3. The original purpose
of the project was to create a simple learning emulator that was well
documented and coded in terms that were easy to understand. It was also an
exercise to learn more about Python. The result is a simple command-line
based Chip 8 emulator.

In addition to supporting Chip 8 ROMs, the emulator also supports the
[XO Chip](https://johnearnest.github.io/Octo/docs/XO-ChipSpecification.html) 
and [Super Chip](https://github.com/JohnEarnest/Octo/blob/gh-pages/docs/SuperChip.md) specifications.
Note that while there are no special flags that are needed to run an XO Chip,
Super Chip, or normal Chip 8 ROM, there are other compatibility flags that
may need to be set for the ROM to run properly. See the [Quirks Modes](#quirks-modes)
documentation below for more information.
 
There are two other versions of the emulator written in different languages:

* [Chip8Java](https://github.com/craigthomas/Chip8Java)
* [Chip8C](https://github.com/craigthomas/Chip8C)


## License

This project makes use of an MIT style license. Please see the file called LICENSE.


## Installing

Copy the source files to a directory of your choice. In addition to
the source, you will need the following required software packages:

* [Python 3.6.8 or better](http://www.python.org)
* [pygame](http://www.pygame.org)

I strongly recommend creating a virtual environment using the 
[virtualenv](http://pypi.python.org/pypi/virtualenv) builder as well as the
[virtualenvwrapper](https://bitbucket.org/dhellmann/virtualenvwrapper) tools.
With these tools, you can easily create a virtual sandbox to install pygame
and run the emulator in, without touching your master Python environment.


### Ubuntu Installation

The installation under Ubuntu 20.04 requires several different steps:

1. Install SDL libraries. The SDL (Simple DirectMedia Layer) libraries are used by PyGame to draw 
images on the screen. Several other dependencies are needed by SDL in order to install PyGame. 
To install the required SDL libraries (plus dependencies) from the command-line:

    ```
    sudo apt install python3 python3-dev libsdl-dev libfreetype6-dev \
    libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl-sound1.2-dev \
    libportmidi-dev
    ```

2. Install PIP. The `pip` package manager is used for managing Python packages. To install `pip` 
from the command-line:

    ```
    sudo apt install python3-pip
    ```

3. (*Optional*) Install virtual environment support for Python:

   1. Install virtual environment support:

      ```
      pip3 install virtualenv
      pip3 install virtualenvwrapper
      ```

   2. First you must update your `.bashrc` file in the home directory and add a few lines 
   to the bottom of that file:

      ```
      cat >> ~/.bashrc << EOF
      export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
      export WORKON_HOME=$HOME/.virtualenvs
      export PATH=$PATH:$HOME/.local/bin
      source $HOME/.local/bin/virtualenvwrapper.sh
      EOF
      ```

   3. Next you must source the `.bashrc` file:

      ```
      source ~/.bashrc
      ```

   4. Finally, you can create the environment:

      ```
      mkvirtualenv chip8
      ```

4. Clone (or download) the Chip 8 emulator project:

    ```
    sudo apt install git
    git clone https://github.com/craigthomas/Chip8Python.git
    ```

5. Install the requirements from the project:

    ```
    pip install -r requirements.txt
    ```


### Windows Installation

1. Download and install [Python 3.6.8 for Windows](https://www.python.org/downloads/release/python-368/). 
Make sure that `pip` and `Add python.exe to Path` options are checked when performing the installation. Later
versions of Python 3 are also likely to work correctly with the emulator.

2. (*Optional*) Install virtual environment support for Python. Run the following commands from a command prompt:

    1. Install the virtual environment wrapper:

    ```
    pip install virtualenv
    pip install virtualenvwrapper-win
    ```

   2. Create a new environment for the Chip 8 emulator:

      ```
      mkvirtualenv chip8
      ```

3. Install [Git for Windows](https://git-scm.com/download/win).

4. Clone (or download) the source files from GitHub. Run the following commands in a command prompt window:

    ```
    git clone https://github.com/craigthomas/Chip8Python.git
    ```

5. Install the requirements for the project. Run the following commands in a command prompt window 
in the directory where you cloned or downloaded the source files:

    ```
    pip install -r requirements.txt
    ```


## Running

### Running a ROM

Note that if you created a virtual environment as detailed above, 
you will need to `workon` that environment before starting the emulator:

    workon chip8
    
The command-line interface requires a single argument, which is the full
path to a Chip 8 ROM. Run the following command in the directory where you 
cloned or downloaded the source files:

    python yac8e.py /path/to/rom/filename

This will start the emulator with the specified ROM. 

### Screen Scale

The `--scale` switch will scale the size of the window (the original size at 1x
scale is 64 x 32):

    python yac8e.py /path/to/rom/filename --scale 10

The command above will scale the window so that it is 10 times the normal
size.

### Instructions Per Second

The `--ticks` switch will limit the number of instructions per second that the 
emulator is allowed to run. By default, the value is set to 1,000. Minimum values 
are 200. Use this switch to adjust the running time of ROMs that execute too quickly. 
For simplicity, each instruction is assumed to take the same amount of time.

    python yac8e.py /path/to/rom/filename --ticks 2000   

### Quirks Modes

Over time, various extensions to the Chip8 mnemonics were developed, which
resulted in an interesting fragmentation of the Chip8 language specification.
As discussed in Octo's [Mastering SuperChip](https://github.com/JohnEarnest/Octo/blob/gh-pages/docs/SuperChip.md)
documentation, one version of the SuperChip instruction set subtly changed
the meaning of a few instructions from their original Chip8 definitions.
This change went mostly unnoticed for many implementations of the Chip8
langauge. Problems arose when people started writing programs using the
updated language model - programs written for "pure" Chip8 ceased to 
function correctly on emulators making use of the altered specification.

To address this issue, [Octo](https://github.com/JohnEarnest/Octo) implements
a number of _quirks_ modes so that all Chip8 software can run correctly, 
regardless of which specification was used when developing the Chip8 program.
This same approach is used here, such that there are several `quirks` flags
that can be passed to the emulator at startup to force it to run with 
adjustments to the language specification.

Additional quirks and their impacts on the running Chip8 interpreter are 
examined in great depth at Chromatophore's [HP48-Superchip](https://github.com/Chromatophore/HP48-Superchip)
repository. Many thanks for this detailed explanation of various quirks 
found in the wild!

#### Shift Quirks

The `--shift_quirks` flag will change the way that register shift operations work.
In the original language specification two registers were required: the 
destination register `x`, and the source register `y`. The source register `y` 
value was shifted one bit left or right, and stored in `x`. For example, 
shift left was defined as:

    Vx = Vy << 1

However, with the updated language specification, the source and destination
register are assumed to always be the same, thus the `y` register is ignored and
instead the value is sourced from `x` as such:

    Vx = Vx << 1


#### Index Quirks

The `--index_quirks` flag controls whether post-increments are made to the index register
following various register based operaitons. For  load (`Fn65`) and store (`Fn55`) register 
operations, the original specification for the Chip8 language results in the index 
register being post-incremented by the number of registers stored. With the Super 
Chip8 specification, this behavior is not always adhered to. Setting `--index_quirks` 
will prevent the post-increment of the index register from occurring after either of these 
instructions.


#### Jump Quirks

The `--jump_quirks` controls how jumps to various addresses are made with the jump (`Bnnn`)
instruction. In the original Chip8 language specification, the jump is made by taking the
contents of register 0, and adding it to the encoded numeric value, such as:

    PC = V0 + nnn

With the Super Chip8 specification, the highest 4 bits of the instruction encode the 
register to use (`Bxnn`) such. The behavior of `--jump_quirks` becomes:

    PC = Vx + nn


#### Clip Quirks

The `--clip_quirks` controls whether sprites are allowed to wrap around the display.
By default, sprits will wrap around the borders of the screen. If turned on, then 
sprites will not be allowed to wrap.


#### Logic Quirks

The `--logic_quirks` controls whether the F register is cleared after logic operations
such as AND, OR, and XOR. By default, F is left undefined following these operations.
With the flag turned on, F will always be cleared.


### Memory Size

The original specification of the Chip8 language defined a 4K memory size for the
interpreter. The addition of the XO Chip extensions require a 64K memory size
for the interpreter. By default, the interpreter will start with a 64K memory size,
but this behavior can be controlled with the `--mem_size` flag. Valid options are
`64K` or `4K` for historical purposes.


### Colors

The original Chip8 language specification called for pixels to be turned on or 
off. It did not specify what color the pixel states had to be. The emulator 
lets the user specify what colors they want to use when the emulator is running.
Color values are specified by using HTML hex values such as `AABBCC` without the
leading `#`. There are currently 4 color values that can be set:

* `--color_0` specifies the background color. This defaults to `000000`.
* `--color_1` specifies bitplane 1 color. This defaults to `FF33CC`.
* `--color_2` specifies bitplane 2 color. This defaults to `33CCFF`.
* `--color_3` specifies bitplane 1 and 2 overlap color. This defaults to `FFFFFF`.

For Chip8 and SuperChip 8 programs, only the background color `color_0` (for pixels
turned off) and the bitplane 1 color `color_1` (for pixels turned on) are used.
Only XO Chip programs will use `color_2` and `color_3` when the additional bitplanes
are potentially used.


## Customization

The file `chip8/config.py` contains several variables that can be changed to
customize the operation of the emulator.  The Chip 8 has 16 keys:

### Keys

The original Chip 8 had a keypad with the numbered keys 0 - 9 and A - F (16
keys in total). The original key configuration was as follows:


| `1` | `2` | `3` | `C` |
|-----|-----|-----|-----|
| `4` | `5` | `6` | `D` |
| `7` | `8` | `9` | `E` |
| `A` | `0` | `B` | `F` |

The Chip8 emulator maps them to the following keyboard keys by default:

| `1` | `2` | `3` | `4` |
|-----|-----|-----|-----|
| `Q` | `W` | `E` | `R` |
| `A` | `S` | `D` | `F` |
| `Z` | `X` | `C` | `V` |

If you wish to configure a different key-mapping, simply change the `KEY_MAPPINGS` variable
in the configuration file to reflect the mapping that you want. The
[pygame.key](https://www.pygame.org/docs/ref/key.html) documentation contains a
list of all the valid constants for keyboard key values.

### Debug Keys

In addition to the key mappings specified in the configuration file, there are additional
keys that impact the execution of the emulator.

| Keyboard Key | Effect             |
| :----------: |--------------------|
| `ESC`        | Quits the emulator |


## ROM Compatibility

Here are the list of public domain ROMs and their current status with the emulator, along 
with links to public domain repositories where applicable.

### Chip 8 ROMs

| ROM Name                                                                                          |      Working       |     Flags     | 
|:--------------------------------------------------------------------------------------------------|:------------------:|:-------------:|
| [1D Cellular Automata](https://johnearnest.github.io/chip8Archive/play.html?p=1dcell)             | :heavy_check_mark: |               |
| [8CE Attourny - Disc 1](https://johnearnest.github.io/chip8Archive/play.html?p=8ceattourny_d1)    | :heavy_check_mark: |               |
| [8CE Attourny - Disc 2](https://johnearnest.github.io/chip8Archive/play.html?p=8ceattourny_d2)    | :heavy_check_mark: |               |
| [8CE Attourny - Disc 3](https://johnearnest.github.io/chip8Archive/play.html?p=8ceattourny_d3)    | :heavy_check_mark: |               |
| [Bad Kaiju Ju](https://johnearnest.github.io/chip8Archive/play.html?p=BadKaiJuJu)                 | :heavy_check_mark: |               |
| [Br8kout](https://johnearnest.github.io/chip8Archive/play.html?p=br8kout)                         | :heavy_check_mark: |               |
| [Carbon8](https://johnearnest.github.io/chip8Archive/play.html?p=carbon8)                         | :heavy_check_mark: |               |
| [Cave Explorer](https://johnearnest.github.io/chip8Archive/play.html?p=caveexplorer)              | :heavy_check_mark: |               |
| [Chipquarium](https://johnearnest.github.io/chip8Archive/play.html?p=chipquarium)                 | :heavy_check_mark: |               |
| [Danm8ku](https://johnearnest.github.io/chip8Archive/play.html?p=danm8ku)                         | :heavy_check_mark: |               |
| [down8](https://johnearnest.github.io/chip8Archive/play.html?p=down8)                             | :heavy_check_mark: |               |
| [Falling Ghosts](https://veganjay.itch.io/falling-ghosts)                                         | :heavy_check_mark: |               |
| [Flight Runner](https://johnearnest.github.io/chip8Archive/play.html?p=flightrunner)              | :heavy_check_mark: |               |
| [Fuse](https://johnearnest.github.io/chip8Archive/play.html?p=fuse)                               | :heavy_check_mark: |               |
| [Ghost Escape](https://johnearnest.github.io/chip8Archive/play.html?p=ghostEscape)                | :heavy_check_mark: |               | 
| [Glitch Ghost](https://johnearnest.github.io/chip8Archive/play.html?p=glitchGhost)                | :heavy_check_mark: |               |
| [Horse World Online](https://johnearnest.github.io/chip8Archive/play.html?p=horseWorldOnline)     | :heavy_check_mark: |               |
| [Invisible Man](https://mremerson.itch.io/invisible-man)                                          | :heavy_check_mark: | `clip_quirks` |
| [Knumber Knower](https://internet-janitor.itch.io/knumber-knower)                                 | :heavy_check_mark: |               | 
| [Masquer8](https://johnearnest.github.io/chip8Archive/play.html?p=masquer8)                       | :heavy_check_mark: |               |
| [Mastermind](https://johnearnest.github.io/chip8Archive/play.html?p=mastermind)                   | :heavy_check_mark: |               |
| [Mini Lights Out](https://johnearnest.github.io/chip8Archive/play.html?p=mini-lights-out)         | :heavy_check_mark: |               |
| [Octo: a Chip 8 Story](https://johnearnest.github.io/chip8Archive/play.html?p=octoachip8story)    | :heavy_check_mark: |               |
| [Octogon Trail](https://tarsi.itch.io/octogon-trail)                                              | :heavy_check_mark: |               |
| [Octojam 1 Title](https://johnearnest.github.io/chip8Archive/play.html?p=octojam1title)           | :heavy_check_mark: |               |
| [Octojam 2 Title](https://johnearnest.github.io/chip8Archive/play.html?p=octojam2title)           | :heavy_check_mark: |               |
| [Octojam 3 Title](https://johnearnest.github.io/chip8Archive/play.html?p=octojam3title)           | :heavy_check_mark: |               |
| [Octojam 4 Title](https://johnearnest.github.io/chip8Archive/play.html?p=octojam4title)           | :heavy_check_mark: |               |
| [Octojam 5 Title](https://johnearnest.github.io/chip8Archive/play.html?p=octojam5title)           | :heavy_check_mark: |               |
| [Octojam 6 Title](https://johnearnest.github.io/chip8Archive/play.html?p=octojam6title)           | :heavy_check_mark: |               |
| [Octojam 7 Title](https://johnearnest.github.io/chip8Archive/play.html?p=octojam7title)           | :heavy_check_mark: |               |
| [Octojam 8 Title](https://johnearnest.github.io/chip8Archive/play.html?p=octojam8title)           | :heavy_check_mark: |               |
| [Octojam 9 Title](https://johnearnest.github.io/chip8Archive/play.html?p=octojam9title)           | :heavy_check_mark: |               |
| [Octojam 10 Title](https://johnearnest.github.io/chip8Archive/play.html?p=octojam10title)         | :heavy_check_mark: |               |
| [Octo Rancher](https://johnearnest.github.io/chip8Archive/play.html?p=octorancher)                | :heavy_check_mark: |               |
| [Outlaw](https://johnearnest.github.io/chip8Archive/play.html?p=outlaw)                           | :heavy_check_mark: |               |
| [Pet Dog](https://johnearnest.github.io/chip8Archive/play.html?p=petdog)                          | :heavy_check_mark: |               | 
| [Piper](https://johnearnest.github.io/chip8Archive/play.html?p=piper)                             | :heavy_check_mark: |               | 
| [Pumpkin "Dress" Up](https://johnearnest.github.io/chip8Archive/play.html?p=pumpkindressup)       | :heavy_check_mark: |               |
| [RPS](https://johnearnest.github.io/chip8Archive/play.html?p=RPS)                                 | :heavy_check_mark: |               |
| [Slippery Slope](https://johnearnest.github.io/chip8Archive/play.html?p=slipperyslope)            | :heavy_check_mark: |               |
| [Snek](https://johnearnest.github.io/chip8Archive/play.html?p=snek)                               | :heavy_check_mark: |               |
| [Space Jam](https://johnearnest.github.io/chip8Archive/play.html?p=spacejam)                      | :heavy_check_mark: |               |
| [Spock Paper Scissors](https://johnearnest.github.io/chip8Archive/play.html?p=spockpaperscissors) | :heavy_check_mark: |               |
| [Super Pong](https://johnearnest.github.io/chip8Archive/play.html?p=superpong)                    | :heavy_check_mark: |               |
| [Tank!](https://johnearnest.github.io/chip8Archive/play.html?p=tank)                              | :heavy_check_mark: |               |
| [TOMB STON TIPP](https://johnearnest.github.io/chip8Archive/play.html?p=tombstontipp)             | :heavy_check_mark: |               |
| [WDL](https://johnearnest.github.io/chip8Archive/play.html?p=wdl)                                 | :heavy_check_mark: |               |

### Super Chip ROMs

| ROM Name                                                                                     |      Working       | Flags | 
|:---------------------------------------------------------------------------------------------|:------------------:|:-----:|
| [Applejak](https://johnearnest.github.io/chip8Archive/play.html?p=applejak)                  | :heavy_check_mark: |       |
| [Bulb](https://johnearnest.github.io/chip8Archive/play.html?p=bulb)                          | :heavy_check_mark: |       |
| [Black Rainbow](https://johnearnest.github.io/chip8Archive/play.html?p=blackrainbow)         | :heavy_check_mark: |       |
| [Chipcross](https://tobiasvl.itch.io/chipcross)                                              | :heavy_check_mark: |       |
| [Chipolarium](https://tobiasvl.itch.io/chipolarium)                                          | :heavy_check_mark: |       |
| [Collision Course](https://ninjaweedle.itch.io/collision-course)                             | :heavy_check_mark: |       |
| [Dodge](https://johnearnest.github.io/chip8Archive/play.html?p=dodge)                        | :heavy_check_mark: |       |
| [DVN8](https://johnearnest.github.io/chip8Archive/play.html?p=DVN8)                          | :heavy_check_mark: |       |
| [Eaty the Alien](https://johnearnest.github.io/chip8Archive/play.html?p=eaty)                | :heavy_check_mark: |       |
| [Grad School Simulator 2014](https://johnearnest.github.io/chip8Archive/play.html?p=gradsim) | :heavy_check_mark: |       |
| [Horsey Jump](https://johnearnest.github.io/chip8Archive/play.html?p=horseyJump)             | :heavy_check_mark: |       |
| [Knight](https://johnearnest.github.io/chip8Archive/play.html?p=knight)                      |        :x:         |       |
| [Mondri8](https://johnearnest.github.io/chip8Archive/play.html?p=mondri8)                    | :heavy_check_mark: |       |
| [Octopeg](https://johnearnest.github.io/chip8Archive/play.html?p=octopeg)                    | :heavy_check_mark: |       |
| [Octovore](https://johnearnest.github.io/chip8Archive/play.html?p=octovore)                  | :heavy_check_mark: |       |
| [Rocto](https://johnearnest.github.io/chip8Archive/play.html?p=rockto)                       | :heavy_check_mark: |       |
| [Sens8tion](https://johnearnest.github.io/chip8Archive/play.html?p=sens8tion)                | :heavy_check_mark: |       |
| [Snake](https://johnearnest.github.io/chip8Archive/play.html?p=snake)                        | :heavy_check_mark: |       |
| [Squad](https://johnearnest.github.io/chip8Archive/play.html?p=squad)                        | :heavy_check_mark: |       |
| [Sub-Terr8nia](https://johnearnest.github.io/chip8Archive/play.html?p=sub8)                  | :heavy_check_mark: |       |
| [Super Octogon](https://johnearnest.github.io/chip8Archive/play.html?p=octogon)              | :heavy_check_mark: |       |
| [Super Square](https://johnearnest.github.io/chip8Archive/play.html?p=supersquare)           | :heavy_check_mark: |       |
| [The Binding of COSMAC](https://johnearnest.github.io/chip8Archive/play.html?p=binding)      | :heavy_check_mark: |       |
| [Turnover '77](https://johnearnest.github.io/chip8Archive/play.html?p=turnover77)            | :heavy_check_mark: |       |

### XO Chip ROMs

| ROM Name                                                                                              |      Working       | Flags | 
|:------------------------------------------------------------------------------------------------------|:------------------:|:-----:|
| [An Evening to Die For](https://johnearnest.github.io/chip8Archive/play.html?p=anEveningToDieFor)     | :heavy_check_mark: |       |
| [Business Is Contagious](https://johnearnest.github.io/chip8Archive/play.html?p=businessiscontagious) | :heavy_check_mark: |       |
| [Chicken Scratch](https://johnearnest.github.io/chip8Archive/play.html?p=chickenScratch)              | :heavy_check_mark: |       |
| [Civiliz8n](https://johnearnest.github.io/chip8Archive/play.html?p=civiliz8n)                         | :heavy_check_mark: |       |
| [Flutter By](https://johnearnest.github.io/chip8Archive/play.html?p=flutterby)                        | :heavy_check_mark: |       |
| [Into The Garlicscape](https://johnearnest.github.io/chip8Archive/play.html?p=garlicscape)            | :heavy_check_mark: |       |
| [jub8 Song 1](https://johnearnest.github.io/chip8Archive/play.html?p=jub8-1)                          | :heavy_check_mark: |       |
| [jub8 Song 2](https://johnearnest.github.io/chip8Archive/play.html?p=jub8-2)                          | :heavy_check_mark: |       |
| [Kesha Was Biird](https://johnearnest.github.io/chip8Archive/play.html?p=keshaWasBiird)               | :heavy_check_mark: |       |
| [Kesha Was Niinja](https://johnearnest.github.io/chip8Archive/play.html?p=keshaWasNiinja)             | :heavy_check_mark: |       |
| [Octo paint](https://johnearnest.github.io/chip8Archive/play.html?p=octopaint)                        | :heavy_check_mark: |       |
| [Octo Party Mix!](https://johnearnest.github.io/chip8Archive/play.html?p=OctoPartyMix)                | :heavy_check_mark: |       |
| [Octoma](https://johnearnest.github.io/chip8Archive/play.html?p=octoma)                               | :heavy_check_mark: |       |
| [Red October V](https://johnearnest.github.io/chip8Archive/play.html?p=redOctober)                    | :heavy_check_mark: |       |
| [Skyward](https://johnearnest.github.io/chip8Archive/play.html?p=skyward)                             | :heavy_check_mark: |       |
| [Spock Paper Scissors](https://johnearnest.github.io/chip8Archive/play.html?p=spockpaperscissors)     | :heavy_check_mark: |       |
| [T8NKS](https://johnearnest.github.io/chip8Archive/play.html?p=t8nks)                                 | :heavy_check_mark: |       |
| [Tapeworm](https://tarsi.itch.io/tapeworm)                                                            | :heavy_check_mark: |       |
| [Truck Simul8or](https://johnearnest.github.io/chip8Archive/play.html?p=trucksimul8or)                | :heavy_check_mark: |       |
| [SK8 H8 1988](https://johnearnest.github.io/chip8Archive/play.html?p=sk8)                             | :heavy_check_mark: |       |
| [Super NeatBoy](https://johnearnest.github.io/chip8Archive/play.html?p=superneatboy)                  | :heavy_check_mark: |       |
| [Wonky Pong](https://johnearnest.github.io/chip8Archive/play.html?p=wonkypong)                        | :heavy_check_mark: |       |


## Further Documentation

The best documentation is in the code itself. Please feel free to examine the
code and experiment with it. 

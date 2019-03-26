# Yet Another (Super) Chip 8 Emulator

[![Build Status](https://travis-ci.org/craigthomas/Chip8Python.svg?branch=master)](https://travis-ci.org/craigthomas/Chip8Python) 
[![codecov](https://codecov.io/gh/craigthomas/Chip8Python/branch/master/graph/badge.svg)](https://codecov.io/gh/craigthomas/Chip8Python) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/f100b6deb9bf4729a2c55ef12fb695c9)](https://www.codacy.com/app/craig-thomas/Chip8Python?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=craigthomas/Chip8Python&amp;utm_campaign=Badge_Grade)
[![Dependency Status](https://dependencyci.com/github/craigthomas/Chip8Python/badge?style=flat)](https://dependencyci.com/github/craigthomas/Chip8Python)


## Table of Contents

1. [What is it?](#what-is-it)
2. [License](#license)
3. [Installing](#installing)
    1. [Ubuntu Installation](#ubuntu-installation)
    2. [Windows Installation](#windows)
4. [Running](#running)
    1. [Running a ROM](#running-a-rom)
    2. [Screen Scale](#screen-scale)
    3. [Execution Delay](#execution-delay)
5. [Customization](#customization)
    1. [Keys](#keys)
    2. [Debug Keys](#debug-keys)
6. [Further Documentation](#further-documentation)

## What is it?

This project is a Chip 8 emulator written in Python 2.7. The original purpose
of the project was to create a simple learning emulator that was well
documented and coded in terms that were easy to understand. It was also an
exercise to learn more about Python. The result is a simple command-line
based Chip 8 emulator.

In addition to supporting Chip 8 ROMs, the emulator also supports the
Super Chip 8 instruction set. Note that no additional configuration is
needed to run a Super Chip 8 ROM - simply run the ROM the same way you
would run a normal Chip 8 ROM.


## License

Please see the file called LICENSE.


## Installing

Copy the source files to a directory of your choice. In addition to
the source, you will need the following required software packages:

* [Python 2.7](http://www.python.org)
* [pygame](http://www.pygame.org)

I strongly recommend creating a virtual environment using the 
[virtualenv](http://pypi.python.org/pypi/virtualenv) builder as well as the
[virtualenvwrapper](https://bitbucket.org/dhellmann/virtualenvwrapper) tools.
With these tools, you can easily create a virtual sandbox to install pygame
and run the emulator in, without touching your master Python environment.


### Ubuntu Installation

The installation under Ubuntu requires several different steps:

1. Install SDL libraries. The SDL (Simple DirectMedia Layer) libraries are used by PyGame to draw 
images on the screen. Several other dependencies are needed by SDL in order to install PyGame. 
To install the required SDL libraries (plus dependencies) from the command-line:

    ```
    sudo apt-get install libfreetype6-dev libsdl-dev libsdl-image1.2-dev \ 
    libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl-sound1.2-dev \
    libportmidi-dev python-dev
    ```

2. Install PIP. The `pip` package manager is used for managing Python packages. To install `pip` 
from the command-line:

    ```
    sudo apt-get install python-pip
    ```

3. (*Optional*) Install virtual environment support for Python:

    1. Install virtual environment support:

    ```
    pip install virtualenv
    pip install virtualenvwrapper
    ```

    2. First you must update your `.bashrc` file in the your home directory and add a few lines 
    to the bottom of that file:

    ```
    cat >> ~/.bashrc << EOF
    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh
    EOF
    ```

    3. Next you must source the `.bashrc` file:

    ```
    source ~/.bashrc
    ```

    4. Finally you can create the environment:

    ```
    mkvirtualenv chip8
    ```

5. Clone (or download) the Chip 8 emulator project:

    ```
    sudo apt-get install git
    git clone https://github.com/craigthomas/Chip8Python.git
    ```

6. Install the requirements from the project:

    ```
    pip install -r requirements.txt
    ```


### Windows Installation

1. Download and install [Python 2.7.15 for Windows](https://www.python.org/downloads/release/python-2715/). 
Make sure that `pip` and `Add python.exe to Path` options are checked when performing the installation.

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

4. Install [Git for Windows](https://git-scm.com/download/win).

5. Clone (or download) the source files from GitHub. Run the following commands in a command prompt window:

    ```
    git clone https://github.com/craigthomas/Chip8Python.git
    ```

6. Install the requirements for the project. Run the following commands in a command prompt window 
in the directory where you cloned or downloaded the source files:

    ```
    pip install -r requirements.txt
    ```


## Running

### Running a ROM

The command-line interface requires a single argument, which is the full
path to a Chip 8 ROM. Run the following command in the directory where you 
cloned or downloaded the source files:

    python chip8/yac8e.py /path/to/rom/filename

This will start the emulator with the specified ROM. Note that if you created 
a virtual environment as detailed above, you will need to `workon` that 
environment before starting the emulator:

    workon chip8

### Screen Scale

The `-s` switch will scale the size of the window (the original size at 1x
scale is 64 x 32):

    python chip8/yac8e.py /path/to/rom/filename -s 10

The command above will scale the window so that it is 10 times the normal
size.

### Execution Delay

You may also wish to experiment with the `-d` switch, which instructs
the emulator to add a delay to every operation that is executed. For example,

    python chip8/yac8e.py /path/to/rom/filename -d 10

The command above will add a 10 ms delay to every opcode that is executed.
This is useful for very fast computers (note that it is difficult to find
information regarding opcode execution times, as such, I have not attempted
any fancy timing mechanisms to ensure that instructions are executed in a
set amount of time).


## Customization

The file `chip8/config.py` contains several variables that can be changed to
customize the operation of the emulator.  The Chip 8 has 16 keys:

### Keys

The original Chip 8 had a keypad with the numbered keys 0 - 9 and A - F (16
keys in total). Without any modifications to the emulator, the keys are mapped
as follows:

| Chip 8 Key | Keyboard Key |
| :--------: | :----------: |
| `1`        | `4`          |
| `2`        | `5`          |
| `3`        | `6`          |
| `4`        | `7`          |
| `5`        | `R`          |
| `6`        | `T`          |
| `7`        | `Y`          |
| `8`        | `U`          |
| `9`        | `F`          |
| `0`        | `G`          |
| `A`        | `H`          |
| `B`        | `J`          |
| `C`        | `V`          |
| `D`        | `B`          |
| `E`        | `N`          |
| `F`        | `M`          |

If you wish to configure a different key-mapping, simply change the `KEY_MAPPINGS` variable
in the configuration file to reflect the mapping that you want. The
[pygame.key](https://www.pygame.org/docs/ref/key.html) documentation contains a
list of all the valid constants for keyboard key values.

### Debug Keys

In addition to the key mappings specified in the configuration file, there are additional
keys that impact the execution of the emulator.

| Keyboard Key | Effect |
| :----------: | ------ |
| `ESC`        | Quits the emulator             |


## Further Documentation

The best documentation is in the code itself. Please feel free to examine the
code and experiment with it. 

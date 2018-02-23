# Yet Another (Super) Chip 8 Emulator

[![Build Status](https://travis-ci.org/craigthomas/Chip8Python.svg?branch=master)](https://travis-ci.org/craigthomas/Chip8Python) 
[![codecov](https://codecov.io/gh/craigthomas/Chip8Python/branch/master/graph/badge.svg)](https://codecov.io/gh/craigthomas/Chip8Python) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/f100b6deb9bf4729a2c55ef12fb695c9)](https://www.codacy.com/app/craig-thomas/Chip8Python?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=craigthomas/Chip8Python&amp;utm_campaign=Badge_Grade)
[![Dependency Status](https://dependencyci.com/github/craigthomas/Chip8Python/badge)](https://dependencyci.com/github/craigthomas/Chip8Python)

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
* [pygame](http://http://www.pygame.org)

I strongly recommend creating a virtual environment using the 
[virtualenv](http://pypi.python.org/pypi/virtualenv) builder as well as the
[virtualenvwrapper](https://bitbucket.org/dhellmann/virtualenvwrapper) tools.
With these tools, you can easily create a virtual sandbox to install pygame
and run the emulator in, without touching your master Python environment.

### Ubuntu Installation

The installation under Ubuntu requires several different steps:

1) Install SDL libraries. The SDL (Simple DirectMedia Layer) libraries are 
used by PyGame to draw images on the screen. Several other dependencies are
needed by SDL in order to install PyGame. To install the required SDL 
libraries (plus dependencies) from the command-line:

        sudo apt-get install libfreetype6-dev libsdl-dev libsdl-image1.2-dev \ 
        libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl-sound1.2-dev \
        libportmidi-dev python-dev
    
2) Install Mercurial. The `hg` command-line tool is required when using 
`pip` (see next step) to install the requirements for the project. To
install Mercurial from the command-line:

        sudo apt-get install mercurial
    
3) Install PIP. The `pip` package manager is used for managing Python
packages. To install `pip` from the command-line:

        sudo apt-get install wget
        wget https://bootstrap.pypa.io/get-pip.py
        sudo python ./get-pip.py
        
4) Clone (or download) the Chip 8 emulator project:

        sudo apt-get install git
        git clone git@github.com:craigthomas/Chip8Python.git
        
5) Install the requirements from the project:

        pip install -r requirements.txt


## Running

### Running a ROM

The command-line interface requires a single argument, which is the full
path to a Chip 8 ROM:

    python chip8/yac8e.py /path/to/rom/filename

This will start the emulator with the specified ROM.

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
customize the operation of the emulator. The most important one is the 
`KEY_MAPPINGS` variable. The Chip 8 has 16 keys:

* The keys 0-9
* The letters A-F

The default configuration of the emulator will map the keypad numeric keys
0-9 to the keys 0-9, and the keyboard keys a-f onto A-F. If you wish to 
configure a different key-mapping, simply change the variable to reflect
the mapping that you want. The [pygame.key](http://pygame.readthedocs.org/en/latest/ref/key.html)
documentation contains a list of all the valid constants for keyboard
key values.


## Further Documentation

The best documentation is in the code itself. Please feel free to examine the
code and experiment with it. 

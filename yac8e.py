#!/usr/bin/env python
"""
Copyright (C) 2024 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A simple Chip 8 emulator - see the README file for more information.
"""
# I M P O R T S ###############################################################

import argparse
import os

# G L O B A L S ###############################################################

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# F U N C T I O N S  ##########################################################


def parse_arguments():
    """
    Parses the command-line arguments passed to the emulator.

    :return: the parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Starts a simple Chip 8 "
        "emulator. See README.md for more information, and LICENSE for "
        "terms of use.")
    parser.add_argument(
        "rom", help="the ROM file to load on startup")
    parser.add_argument(
        "--scale", help="the scale factor to apply to the display "
        "(default is 5)", type=int, default=5, dest="scale")
    parser.add_argument(
        "--delay", help="sets the CPU operation to take at least "
        "the specified number of milliseconds to execute (default is 1)",
        type=int, default=1, dest="op_delay")
    parser.add_argument(
        "--shift_quirks", help="Enable shift quirks",
        action="store_true", dest="shift_quirks"
    )
    parser.add_argument(
        "--index_quirks", help="Enable index quirks",
        action="store_true", dest="index_quirks"
    )
    parser.add_argument(
        "--jump_quirks", help="Enable jump quirks",
        action="store_true", dest="jump_quirks"
    )
    parser.add_argument(
        "--clip_quirks", help="Enable screen clipping quirks",
        action="store_true", dest="clip_quirks"
    )
    parser.add_argument(
        "--logic_quirks", help="Enable logic quirks",
        action="store_true", dest="logic_quirks"
    )
    parser.add_argument(
        "--mem_size", help="Maximum memory size (64K default)",
        dest="mem_size", choices=["4K", "64K"], default="64K"
    )
    parser.add_argument(
        "--trace", help="print registers and instructions to STDOUT",
        action="store_true", dest="trace"
    )
    parser.add_argument(
        "--color_0", help="the hex color to use for the background (default=000000)",
        dest="color_0", default="000000"
    )
    parser.add_argument(
        "--color_1", help="the hex color to use for bitplane 1 (default=666666)",
        dest="color_1", default="666666"
    )
    parser.add_argument(
        "--color_2", help="the hex color to use for bitplane 2 (default=BBBBBB)",
        dest="color_2", default="BBBBBB"
    )
    parser.add_argument(
        "--color_3", help="the hex color to use for bitplane overlaps (default=FFFFFF)",
        dest="color_3", default="FFFFFF"
    )
    return parser.parse_args()


# M A I N #####################################################################

if __name__ == "__main__":
    from chip8.emulator import main_loop
    main_loop(parse_arguments())

# E N D   O F   F I L E #######################################################

"""
Copyright (C) 2012 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A simple Chip 8 emulator - see the README file for more information.
"""
# I M P O R T S ###############################################################

import argparse
import pygame

from config import FONT_FILE, DELAY_INTERVAL
from cpu import Chip8CPU
from screen import Chip8Screen

# C O N S T A N T S ###########################################################

# A simple timer event used for the delay and sound timers
TIMER = pygame.USEREVENT + 1

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
        "-s", help="the scale factor to apply to the display "
        "(default is 5)", type=int, default=5, dest="scale")
    parser.add_argument(
        "-d", help="sets the CPU operation to take at least "
        "the specified number of milliseconds to execute (default is 1)",
        type=int, default=1, dest="op_delay")
    return parser.parse_args()


def main_loop(args):
    """
    Runs the main emulator loop with the specified arguments.

    :param args: the parsed command-line arguments
    """
    screen = Chip8Screen(scale_factor=args.scale)
    screen.init_display()
    cpu = Chip8CPU(screen)
    cpu.load_rom(FONT_FILE, 0)
    cpu.load_rom(args.rom)
    pygame.time.set_timer(TIMER, DELAY_INTERVAL)
    running = True

    while running:
        pygame.time.wait(args.op_delay)
        operand = cpu.execute_instruction()

        # Check for events
        for event in pygame.event.get():
            if event.type == TIMER:
                cpu.decrement_timers()
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                keys_pressed = pygame.key.get_pressed()
                if keys_pressed[pygame.K_q]:
                    running = False

        # Check to see if CPU is in exit state
        if operand == 0x00FD:
            running = False

# M A I N #####################################################################

if __name__ == "__main__":
    main_loop(parse_arguments())

# E N D   O F   F I L E #######################################################

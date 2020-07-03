"""
Copyright (C) 2012-2019 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A simple Chip 8 emulator - see the README file for more information.
"""
# I M P O R T S ###############################################################

import pygame

from chip8.config import FONT_FILE, DELAY_INTERVAL
from chip8.cpu import Chip8CPU
from chip8.screen import Chip8Screen

# C O N S T A N T S ###########################################################

# A simple timer event used for the delay and sound timers
TIMER = pygame.USEREVENT + 1

# F U N C T I O N S  ##########################################################


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

    while cpu.running:
        pygame.time.wait(args.op_delay)
        cpu.execute_instruction()

        # Check for events
        for event in pygame.event.get():
            if event.type == TIMER:
                cpu.decrement_timers()
            if event.type == pygame.QUIT:
                cpu.running = False
            if event.type == pygame.KEYDOWN:
                keys_pressed = pygame.key.get_pressed()
                if keys_pressed[pygame.K_ESCAPE]:
                    cpu.running = False

# E N D   O F   F I L E #######################################################

"""
Copyright (C) 2024 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A simple Chip 8 emulator - see the README file for more information.
"""
# I M P O R T S ###############################################################

import pygame

from chip8.config import FONT_FILE
from chip8.cpu import Chip8CPU
from chip8.screen import Chip8Screen

# F U N C T I O N S  ##########################################################


def main_loop(args):
    """
    Runs the main emulator loop with the specified arguments.

    :param args: the parsed command-line arguments
    """
    delay_timer_event = 24

    screen = Chip8Screen(
        scale_factor=args.scale,
        color_0=args.color_0,
        color_1=args.color_1,
        color_2=args.color_2,
        color_3=args.color_3,
    )
    screen.init_display()
    cpu = Chip8CPU(
        screen,
        shift_quirks=args.shift_quirks,
        index_quirks=args.index_quirks,
        jump_quirks=args.jump_quirks,
        clip_quirks=args.clip_quirks,
        logic_quirks=args.logic_quirks,
        mem_size=args.mem_size,
    )
    cpu.load_rom(FONT_FILE, 0)
    cpu.load_rom(args.rom)

    pygame.init()
    pygame.time.set_timer(delay_timer_event, 17)

    while cpu.running:
        pygame.time.wait(args.op_delay)

        if not cpu.awaiting_keypress:
            cpu.execute_instruction()

        if args.trace:
            print(cpu)

        # # Check for events of specific types
        for event in pygame.event.get():
            if event.type == delay_timer_event:
                cpu.decrement_timers()
            if event.type == pygame.QUIT:
                cpu.running = False
            if event.type == pygame.KEYDOWN:
                keys_pressed = pygame.key.get_pressed()
                if keys_pressed[pygame.K_ESCAPE]:
                    cpu.running = False
                if cpu.awaiting_keypress:
                    cpu.decode_keypress_and_continue(keys_pressed)

# E N D   O F   F I L E #######################################################

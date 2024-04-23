"""
Copyright (C) 2024 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A simple Chip 8 emulator - see the README file for more information.
"""
# I M P O R T S ###############################################################

import pygame

# C U S T O M I Z A T I O N    V A R I A B L E S###############################

# Where the stack pointer should originally point
STACK_POINTER_START = 0x52

# Where the program counter should originally point
PROGRAM_COUNTER_START = 0x200

# Sets which keys on the keyboard map to the Chip 8 keys
KEY_MAPPINGS = {
    0x0: pygame.K_x,
    0x1: pygame.K_1,
    0x2: pygame.K_2,
    0x3: pygame.K_3,
    0x4: pygame.K_q,
    0x5: pygame.K_w,
    0x6: pygame.K_e,
    0x7: pygame.K_a,
    0x8: pygame.K_s,
    0x9: pygame.K_d,
    0xA: pygame.K_z,
    0xB: pygame.K_c,
    0xC: pygame.K_4,
    0xD: pygame.K_r,
    0xE: pygame.K_f,
    0xF: pygame.K_v,
}

# The font file to use
FONT_FILE = "FONTS.chip8"

# Delay timer decrement interval (in ms)
DELAY_INTERVAL = 17

# E N D   O F   F I L E #######################################################

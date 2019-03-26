"""
Copyright (C) 2012-2019 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A simple Chip 8 emulator - see the README file for more information.
"""
# I M P O R T S ###############################################################

import pygame

# C U S T O M I Z A T I O N    V A R I A B L E S###############################

# The total amount of memory to allocate for the emulator
MAX_MEMORY = 4096

# Where the stack pointer should originally point
STACK_POINTER_START = 0x52

# Where the program counter should originally point
PROGRAM_COUNTER_START = 0x200

# Sets which keys on the keyboard map to the Chip 8 keys
KEY_MAPPINGS = {
    0x0: pygame.K_g,
    0x1: pygame.K_4,
    0x2: pygame.K_5,
    0x3: pygame.K_6,
    0x4: pygame.K_7,
    0x5: pygame.K_r,
    0x6: pygame.K_t,
    0x7: pygame.K_y,
    0x8: pygame.K_u,
    0x9: pygame.K_f,
    0xA: pygame.K_h,
    0xB: pygame.K_j,
    0xC: pygame.K_v,
    0xD: pygame.K_b,
    0xE: pygame.K_n,
    0xF: pygame.K_m,
}

# The font file to use
FONT_FILE = "FONTS.chip8"

# Delay timer decrement interval (in ms)
DELAY_INTERVAL = 17

# E N D   O F   F I L E #######################################################

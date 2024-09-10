"""
Copyright (C) 2024 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A Chip 8 CPU - see the README file for more information.
"""
# I M P O R T S ###############################################################

import numpy as np

from pygame import key
from pygame import mixer
from pygame.mixer import Sound
from random import randint

from chip8.config import STACK_POINTER_START, KEY_MAPPINGS, PROGRAM_COUNTER_START

# C O N S T A N T S ###########################################################

# The total number of registers in the Chip 8 CPU
NUM_REGISTERS = 0x10

# The various modes of operation
MODE_NORMAL = 'normal'
MODE_EXTENDED = 'extended'

# Memory sizes available
MEM_SIZE = {
    "4K": 4096,
    "64K": 65536,
}

# The minimum number of audio samples we want to generate. The minimum amount
# of time an audio clip can be played is 1/60th of a second (the frequency
# that the sound timer is decremented). Since we initialize the pygame
# audio mixer to require 48000 samples per second, this means each 1/60th
# of a second requires 800 samples. The audio pattern buffer is only
# 128 bits long, so we will need to repeat it to fill at least 1/60th of a
# second with audio (resampled at the correct frequency). To be safe,
# we'll construct a buffer of at least 4/60ths of a second of
# audio. We can be bigger than the minimum number of samples below, but
# we don't want less than that.
MIN_AUDIO_SAMPLES = 3200

# The audio playback rate to use for Pygame mixer initialization
PYGAME_AUDIO_PLAYBACK_RATE = 48000

# C L A S S E S ###############################################################


class UnknownOpCodeException(Exception):
    """
    A class to raise unknown op code exceptions.
    """
    def __init__(self, op_code):
        Exception.__init__(self, f"Unknown op-code: {op_code:04X}")


class Chip8CPU:
    """
    A class to emulate a Chip 8 CPU. There are several good resources out on
    the web that describe the internals of the Chip 8 CPU. For example:

        http://devernay.free.fr/hacks/chip8/C8TECH10.HTM
        http://michael.toren.net/mirrors/chip8/chip8def.htm

    As usual, a simple Google search will find you other excellent examples.
    To summarize these sources, the Chip 8 has:

        * 16 x 8-bit general purpose registers (V0 - VF**)
        * 1 x 16-bit index register (I)
        * 1 x 16-bit stack pointer (SP)
        * 1 x 16-bit program counter (PC)
        * 1 x 8-bit delay timer (DT)
        * 1 x 8-bit sound timer (ST)

    ** VF is a special register - it is used to store the overflow bit
    """
    def __init__(
            self,
            screen,
            shift_quirks=False,
            index_quirks=False,
            jump_quirks=False,
            clip_quirks=False,
            logic_quirks=False,
            mem_size="64K"
    ):
        """
        Initialize the Chip8 CPU. The only required parameter is a screen
        object that supports the draw_pixel function. For testing purposes,
        this can be set to None.

        :param screen: the screen object to draw pixels on
        :param shift_quirks: enables bit-shift quirks mode
        :param index_quirks: enables index quirks on load/store commands
        :param jump_quirks: enables jump quirks on Bxxx commands
        :param clip_quirks: enables screen clipping quirks
        :param logic_quirks: enables logic quirks
        :param mem_size: sets the maximum memory available "4K" or "64K"
        """
        self.last_pc = 0x0000
        self.last_op = "None"
        self.sound = 0
        self.delay = 0
        self.v = [0] * NUM_REGISTERS
        self.pc = PROGRAM_COUNTER_START
        self.sp = STACK_POINTER_START
        self.index = 0
        self.rpl = [0] * NUM_REGISTERS

        self.pitch = 64
        self.playback_rate = 4000
        self.audio_pattern_buffer = [0] * 16
        self.sound_playing = False
        self.sound_waveform = None

        self.bitplane = 1

        self.shift_quirks = shift_quirks
        self.index_quirks = index_quirks
        self.jump_quirks = jump_quirks
        self.clip_quirks = clip_quirks
        self.logic_quirks = logic_quirks

        self.awaiting_keypress = False
        self.keypress_register = None

        # The operation_lookup table is executed according to the most
        # significant byte of the operand (e.g. operand 8nnn would call
        # self.execute_logical_instruction)
        self.operation_lookup = {
            0x0: self.clear_return,                  # 0nnn - SYS  nnn
            0x1: self.jump_to_address,               # 1nnn - JUMP nnn
            0x2: self.jump_to_subroutine,            # 2nnn - CALL nnn
            0x3: self.skip_if_reg_equal_val,         # 3snn - SKE  Vs, nn
            0x4: self.skip_if_reg_not_equal_val,     # 4snn - SKNE Vs, nn
            0x5: self.save_skip_routines,            # see subfunctions below
            0x6: self.move_value_to_reg,             # 6snn - LOAD Vs, nn
            0x7: self.add_value_to_reg,              # 7snn - ADD  Vs, nn
            0x8: self.execute_logical_instruction,   # see subfunctions below
            0x9: self.skip_if_reg_not_equal_reg,     # 9st0 - SKNE Vs, Vt
            0xA: self.load_index_reg_with_value,     # Annn - LOAD I, nnn
            0xB: self.jump_to_register_plus_value,   # Bnnn - JUMP [V0 + nnn] | [Vx + nnn]
            0xC: self.generate_random_number,        # Ctnn - RAND Vt, nn
            0xD: self.draw_sprite,                   # Dstn - DRAW Vs, Vy, n
            0xE: self.keyboard_routines,             # see subfunctions below
            0xF: self.misc_routines,                 # see subfunctions below
        }

        self.save_skip_lookup = {
            0x0: self.skip_if_reg_equal_reg,         # 5xy0 - SKE  Vx, Vy
            0x2: self.store_subset_regs_in_memory,   # 5xy2 - STORSUB x, y
            0x3: self.read_subset_regs_in_memory,    # 5xy3 - LOADSUB x, y
        }

        self.clear_routines = {
            0xE0: self.clear_screen,                 # 00E0 - CLS
            0xEE: self.return_from_subroutine,       # 00EE - RTS
            0xFB: self.scroll_right,                 # 00FB - SCRR
            0xFC: self.scroll_left,                  # 00FC - SCRL
            0xFD: self.exit,                         # 00FD - EXIT
            0xFE: self.disable_extended_mode,        # 00FE - SET NORMAL
            0xFF: self.enable_extended_mode,         # 00FF - SET EXTENDED
        }

        # This set of operations is invoked when the operand loaded into the
        # CPU starts with 8 (e.g. operand 8nn0 would call
        # self.move_reg_into_reg)
        self.logical_operation_lookup = {
            0x0: self.move_reg_into_reg,             # 8st0 - LOAD Vs, Vt
            0x1: self.logical_or,                    # 8st1 - OR   Vs, Vt
            0x2: self.logical_and,                   # 8st2 - AND  Vs, Vt
            0x3: self.exclusive_or,                  # 8st3 - XOR  Vs, Vt
            0x4: self.add_reg_to_reg,                # 8st4 - ADD  Vs, Vt
            0x5: self.subtract_reg_from_reg,         # 8st5 - SUB  Vs, Vt
            0x6: self.right_shift_reg,               # 8st6 - SHR  Vs
            0x7: self.subtract_reg_from_reg1,        # 8st7 - SUBN Vs, Vt
            0xE: self.left_shift_reg,                # 8stE - SHL  Vs
        }

        # This set of operations is invoked when the operand loaded into the
        # CPU starts with F (e.g. operand Fn07 would call
        # self.move_delay_timer_into_reg)
        self.misc_routine_lookup = {
            0x00: self.index_load_long,                      # F000 - LOADLONG
            0x01: self.set_bitplane,                         # Fn01 - BITPLANE n
            0x02: self.load_audio_pattern_buffer,            # F002 - AUDIO
            0x07: self.move_delay_timer_into_reg,            # Ft07 - LOAD Vt, DELAY
            0x0A: self.wait_for_keypress,                    # Ft0A - KEYD Vt
            0x15: self.move_reg_into_delay_timer,            # Fs15 - LOAD DELAY, Vs
            0x18: self.move_reg_into_sound_timer,            # Fs18 - LOAD SOUND, Vs
            0x1E: self.add_reg_into_index,                   # Fs1E - ADD  I, Vs
            0x29: self.load_index_with_reg_sprite,           # Fs29 - LOAD I, Vs
            0x30: self.load_index_with_extended_reg_sprite,  # Fs30 - LOAD I, Vs
            0x33: self.store_bcd_in_memory,                  # Fs33 - BCD
            0x3A: self.load_pitch,                           # Fx3A - PITCH Vx
            0x55: self.store_regs_in_memory,                 # Fs55 - STOR [I], Vs
            0x65: self.read_regs_from_memory,                # Fs65 - LOAD Vs, [I]
            0x75: self.store_regs_in_rpl,                    # Fs75 - SRPL Vs
            0x85: self.read_regs_from_rpl,                   # Fs85 - LRPL Vs
        }
        self.operand = 0
        self.mode = MODE_NORMAL
        self.screen = screen
        self.memory = bytearray(MEM_SIZE[mem_size])
        self.reset()
        self.running = True
        mixer.init(frequency=PYGAME_AUDIO_PLAYBACK_RATE, size=8, channels=1)

    def __str__(self):
        val = f"PC:{self.last_pc:04X} OP:{self.operand:04X} "
        for index in range(0x10):
            val += f"V{index:X}:{self.v[index]:02X} "
        val += f"I:{self.index:04X} DELAY:{self.delay} SOUND:{self.sound} "
        val += f"{self.last_op}"
        return val

    def execute_instruction(self, operand=None):
        """
        Execute the next instruction pointed to by the program counter.
        For testing purposes, pass the operand directly to the
        function. When the operand is not passed directly to the
        function, the program counter is increased by 2.

        :param operand: the operand to execute
        :return: returns the operand executed
        """
        self.last_pc = self.pc
        if operand:
            self.operand = operand
        else:
            self.operand = int(self.memory[self.pc])
            self.operand = self.operand << 8
            self.operand += int(self.memory[self.pc + 1])
            self.pc += 2
        operation = (self.operand & 0xF000) >> 12
        self.operation_lookup[operation]()
        return self.operand

    def execute_logical_instruction(self):
        """
        Execute the logical instruction based upon the current operand.
        For testing purposes, pass the operand directly to the function.
        """
        operation = self.operand & 0x000F
        try:
            self.logical_operation_lookup[operation]()
        except KeyError:
            raise UnknownOpCodeException(self.operand)

    def keyboard_routines(self):
        """
        Run the specified keyboard routine based upon the operand. These
        operations are:

            Ex9E - SKPR Vx
            ExA1 - SKUP Vx

        0x9E will check to see if the key specified in the x register is
        pressed, and if it is, skips the next instruction. Operation 0xA1 will
        again check for the specified keypress in the x register, and
        if it is NOT pressed, will skip the next instruction. The register
        calculations are as follows:

           Bits:  15-12    11-8      7-4      3-0
                    E        x      9 or A    E or 1
        """
        operation = self.operand & 0x00FF
        x = (self.operand & 0x0F00) >> 8

        key_to_check = self.v[x]
        keys_pressed = key.get_pressed()

        # Skip if the key specified in the source register is pressed
        if operation == 0x9E:
            if key_to_check <= 0xF and keys_pressed[KEY_MAPPINGS[key_to_check]]:
                self.pc += 2
                if self.memory[self.pc - 2] == 0xF0 and self.memory[self.pc - 1] == 0x00:
                    self.pc += 2

        # Skip if the key specified in the source register is not pressed
        if operation == 0xA1:
            if key_to_check <= 0xF and  not keys_pressed[KEY_MAPPINGS[key_to_check]]:
                self.pc += 2
                if self.memory[self.pc - 2] == 0xF0 and self.memory[self.pc - 1] == 0x00:
                    self.pc += 2

    def save_skip_routines(self):
        """
        Will execute either a register save or skip routine.
        """
        operation = self.operand & 0x000F
        try:
            self.save_skip_lookup[operation]()
        except KeyError:
            raise UnknownOpCodeException(self.operand)

    def misc_routines(self):
        """
        Will execute one of the routines specified in misc_routines.
        """
        operation = self.operand & 0x00FF
        try:
            self.misc_routine_lookup[operation]()
        except KeyError:
            raise UnknownOpCodeException(self.operand)

    def clear_return(self):
        """
        Opcodes starting with a 0 usually correspond to screen clearing or scrolling
        routines, or emulator exit routines.
        """
        operation = self.operand & 0x00FF
        sub_operation = operation & 0x00F0
        if sub_operation == 0x00C0:
            num_lines = self.operand & 0x000F
            self.screen.scroll_down(num_lines, self.bitplane)
            self.last_op = f"Scroll Down {num_lines:01X}"
        elif sub_operation == 0x00D0:
            num_lines = self.operand & 0x000F
            self.screen.scroll_up(num_lines, self.bitplane)
            self.last_op = f"Scroll Up {num_lines:01X}"
        else:
            try:
                self.clear_routines[operation]()
            except KeyError:
                raise UnknownOpCodeException(self.operand)

    def clear_screen(self):
        """
        00E0 - CLS

        Clears the screen
        """
        self.screen.clear_screen(self.bitplane)
        self.last_op = "CLS"

    def return_from_subroutine(self):
        """
        00EE - RTS

        Return from subroutine. Pop the current value in the stack pointer
        off of the stack, and set the program counter to the value popped.
        """
        self.sp -= 1
        self.pc = self.memory[self.sp] << 8
        self.sp -= 1
        self.pc += self.memory[self.sp]
        self.last_op = "RTS"

    def scroll_right(self):
        """
        00FB - SCRR

        Scrolls the screen right by 4 pixels.
        """
        self.screen.scroll_right(self.bitplane)
        self.last_op = "Scroll Right"

    def scroll_left(self):
        """
        00FC - SCRL

        Scrolls the screen left by 4 pixels.
        """
        self.screen.scroll_left(self.bitplane)
        self.last_op = "Scroll Left"

    def exit(self):
        """
        00FD - EXIT

        Exits the emulator.
        """
        self.running = False
        self.last_op = "EXIT"

    def disable_extended_mode(self):
        """
        00FE - SET NORMAL

        Disables extended mode.
        """
        self.screen.set_normal()
        self.mode = MODE_NORMAL
        self.last_op = "Set Normal Mode"

    def enable_extended_mode(self):
        """
        00FF - SET EXTENDED

        Set extended mode.
        """
        self.screen.set_extended()
        self.mode = MODE_EXTENDED
        self.last_op = "Set Extended Mode"

    def jump_to_address(self):
        """
        1nnn - JUMP nnn

        Jump to address. The address to jump to is calculated using the bits
        taken from the operand as follows:

           Bits:  15-12   11-8   7-4   3-0
                    1      n      n     n
        """
        self.pc = self.operand & 0x0FFF
        self.last_op = f"JUMP {self.pc:04X}"

    def jump_to_subroutine(self):
        """
        2nnn - CALL nnn

        Jump to subroutine. Save the current program counter on the stack. The
        subroutine to jump to is taken from the operand as follows:

           Bits:  15-12    11-8   7-4   3-0
                    2        n     n     n
        """
        self.memory[self.sp] = self.pc & 0x00FF
        self.sp += 1
        self.memory[self.sp] = (self.pc & 0xFF00) >> 8
        self.sp += 1
        self.pc = self.operand & 0x0FFF
        self.last_op = f"CALL {self.pc:04X}"

    def skip_if_reg_equal_val(self):
        """
        3xnn - SKE Vx, nn

        Skip if register contents equal to constant value. The calculation for
        the register and constant is performed on the operand:

           Bits:  15-12   11-8   7-4   3-0
                    3      x      n     n

        The program counter is updated to skip the next instruction by
        advancing it by 2 bytes.
        """
        x = (self.operand & 0x0F00) >> 8
        if self.v[x] == (self.operand & 0x00FF):
            self.pc += 2
            if self.memory[self.pc - 2] == 0xF0 and self.memory[self.pc - 1] == 0x00:
                self.pc += 2
        self.last_op = f"SKE V{x:01X}, {self.operand & 0x00FF:02X}"

    def skip_if_reg_not_equal_val(self):
        """
        4xnn - SKNE Vx, nn

        Skip if register contents not equal to constant value. The calculation
        for the register and constant is performed on the operand:

           Bits:  15-12   11-8   7-4   3-0
                    4      x      n     n

        The program counter is updated to skip the next instruction by
        advancing it by 2 bytes.
        """
        x = (self.operand & 0x0F00) >> 8
        self.last_op = f"SKNE V{x:X}, {self.operand & 0x00FF:02X} (comparing {self.v[x]:02X} to {self.operand & 0xFF:02X})"
        if self.v[x] != (self.operand & 0x00FF):
            self.pc += 2
            if self.memory[self.pc - 2] == 0xF0 and self.memory[self.pc - 1] == 0x00:
                self.pc += 2

    def skip_if_reg_equal_reg(self):
        """
        5xy0 - SKE Vx, Vy

        Skip if x register is equal to y register. The calculation
        for the registers to use is performed on the operand:

           Bits:  15-12    11-8   7-4   3-0
                    5       x      y     0

        The program counter is updated to skip the next instruction by
        advancing it by 2 bytes.
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        if self.v[x] == self.v[y]:
            self.pc += 2
            if self.memory[self.pc - 2] == 0xF0 and self.memory[self.pc - 1] == 0x00:
                self.pc += 2
        self.last_op = f"SKE V{x:01X}, V{y:01X}"

    def store_subset_regs_in_memory(self):
        """
        5xy2 - STORSUB [I], Vx, Vy

        Store a subset of registers from x to y in memory starting at index.
        The x and y calculation is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         x        y         2

        If x is larger than y, then they will be stored in reverse order.
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        pointer = 0
        if y >= x:
            for z in range(x, y+1):
                self.memory[self.index + pointer] = self.v[z]
                pointer += 1
        else:
            for z in range(x, y-1, -1):
                self.memory[self.index + pointer] = self.v[z]
                pointer += 1

        self.last_op = f"STORSUB [I], {x:01X}, {y:01X}"

    def read_subset_regs_in_memory(self):
        """
        5xy3 - LOADSUB [I], Vx, Vy

        Load a subset of registers from x to y in memory starting at index.
        The x and y calculation is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         x        y         2

        If x is larger than y, then they will be loaded in reverse order.
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        pointer = 0
        if y >= x:
            for z in range(x, y+1):
                self.v[z] = self.memory[self.index + pointer]
                pointer += 1
        else:
            for z in range(x, y-1, -1):
                self.v[z] = self.memory[self.index + pointer]
                pointer += 1

        self.last_op = f"LOADSUB [I], {x:01X}, {y:01X}"

    def move_value_to_reg(self):
        """
        6xnn - LOAD Vx, nn

        Move the constant value into the specified register. The calculation
        for the registers is performed on the operand:

           Bits:  15-12    11-8    7-4   3-0
                    6       x       n     n
        """
        x = (self.operand & 0x0F00) >> 8
        self.v[x] = self.operand & 0x00FF
        self.last_op = f"LOAD V{x:X}, {self.operand & 0x00FF:02X}"

    def add_value_to_reg(self):
        """
        7xnn - ADD Vx, nn

        Add the constant value to the specified register. The calculation
        for the registers is performed on the operand:

           Bits:  15-12     11-8    7-4    3-0
                    7         x      n      n
         """
        x = (self.operand & 0x0F00) >> 8
        self.v[x] = (self.v[x] + (self.operand & 0x00FF)) % 256
        self.last_op = f"ADD V{x:01X}, {self.operand & 0x00FF:02X}"

    def move_reg_into_reg(self):
        """
        8xy0 - LOAD Vx, Vy

        Move the value of the x register into the value of the y
        register. The calculation for the registers is performed on the
        operand:

           Bits:  15-12   11-8    7-4    3-0
                    8       x      y      0
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        self.v[x] = self.v[y]
        self.last_op = f"LOAD V{x:01X}, V{y:01X}"

    def logical_or(self):
        """
        8xy1 - OR   Vx, Vy

        Perform a logical OR operation between the x and the y
        register, and store the result in the x register. The register
        calculations are as follows:

           Bits:  15-12    11-8   7-4    3-0
                    8       x      y      1
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        self.v[x] |= self.v[y]
        if self.logic_quirks:
            self.v[0xF] = 0
        self.last_op = f"OR V{x:01X}, V{y:01X}"

    def logical_and(self):
        """
        8xy2 - AND  Vx, Vy

        Perform a logical AND operation between the x and the y
        register, and store the result in the x register. The register
        calculations are as follows:

           Bits:  15-12   11-8   7-4   3-0
                    8       x     y     2
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        self.v[x] &= self.v[y]
        if self.logic_quirks:
            self.v[0xF] = 0
        self.last_op = f"AND V{x:01X}, V{y:01X}"

    def exclusive_or(self):
        """
        8xy3 - XOR  Vx, Vy

        Perform a logical XOR operation between the x and the y
        register, and store the result in the x register. The register
        calculations are as follows:

           Bits:  15-12   11-8   7-4   3-0
                    8       x     y     3
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        self.v[x] ^= self.v[y]
        if self.logic_quirks:
            self.v[0xF] = 0
        self.last_op = f"XOR V{x:01X}, V{y:01X}"

    def add_reg_to_reg(self):
        """
        8xy4 - ADD  Vx, Vy

        Add the value in the x register to the value in the y
        register, and store the result in the x register. The register
        calculations are as follows:

           Bits:  15-12   11-8   7-4  3-0
                    8       x     y    4

        If a carry is generated, set a carry flag in register VF.
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        carry = 1 if self.v[x] + self.v[y] > 255 else 0
        self.v[x] = (self.v[x] + self.v[y]) % 256
        self.v[0xF] = carry
        self.last_op = f"ADD V{x:01X}, V{y:01X}"

    def subtract_reg_from_reg(self):
        """
        8xy5 - SUB  Vx, Vy

        Subtract the value in the target register from the value in the source
        register, and store the result in the target register. The register
        calculations are as follows:

           Bits:  15-12     11-8    7-4   3-0
                    8        x      y      5

        If a borrow is generated, set a carry flag in register VF.
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        borrow = 1 if self.v[x] >= self.v[y] else 0
        self.v[x] = self.v[x] - self.v[y] if self.v[x] >= self.v[y] else 256 + self.v[x] - self.v[y]
        self.v[0xF] = borrow
        self.last_op = f"SUB V{x:01X}, V{y:01X}"

    def right_shift_reg(self):
        """
        8xy6 - SHR  Vx, (Vy)

        Shift the bits in the y register 1 bit to the right and stores the result
        in the x register. Bit 0 will be shifted into register
        vf. The register calculation is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    8        x         y         6

        If shift_quirks mode is enabled, then register x will be bit shifted and
        stored in x.
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        if self.shift_quirks:
            bit_one = self.v[x] & 0x1
            self.v[x] = self.v[x] >> 1
            self.v[0xF] = bit_one
            self.last_op = f"SHR V{x:01X}"
        else:
            bit_one = self.v[y] & 0x1
            self.v[x] = self.v[y] >> 1
            self.v[0xF] = bit_one
            self.last_op = f"SHR V{x:01X}, V{y:01X}"

    def subtract_reg_from_reg1(self):
        """
        8xy7 - SUBN Vx, Vy

        Subtract the value in the x register from the value in the y
        register, and store the result in the x register. The register
        calculations are as follows:

           Bits:  15-12     11-8      7-4       3-0
                    8        x         y         7

        If a borrow is NOT generated, set a carry flag in register VF.
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        not_borrow = 1 if self.v[y] >= self.v[x] else 0
        self.last_op = f"SUBN V{x:01X} ({self.v[x]:02X}), V{y:01X} ({self.v[y]:02X})"
        self.v[x] = self.v[y] - self.v[x] if self.v[y] >= self.v[x] else 256 + self.v[y] - self.v[x]
        self.v[0xF] = not_borrow

    def left_shift_reg(self):
        """
        8xyE - SHL  Vx, (Vy)

        Shift the bits in the source register 1 bit to the left and
        stores the result in the source register. Bit 7 will be shifted into
        register vf. The register calculation is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    8        x        y         E

        if shift_quirks is set, then the source and destination register
        will always be x.
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        if self.shift_quirks:
            bit_seven = (self.v[x] & 0x80) >> 7
            self.v[x] = (self.v[x] << 1) & 0xFF
            self.v[0xF] = bit_seven
            self.last_op = f"SHL V{x:01X}"
        else:
            bit_seven = (self.v[y] & 0x80) >> 7
            self.v[x] = (self.v[y] << 1) & 0xFF
            self.v[0xF] = bit_seven
            self.last_op = f"SHL V{x:01X}, V{y:01X}"

    def skip_if_reg_not_equal_reg(self):
        """
        9xy0 - SKNE Vx, Vy

        Skip if x register is equal to y register. The calculation
        for the registers to use is performed on the operand:

           Bits:  15-12     11-8      7-4       3-0
                    9         x        y         0

        The program counter is updated to skip the next instruction by
        advancing it by 2 bytes.
        """
        x = (self.operand & 0x0F00) >> 8
        y = (self.operand & 0x00F0) >> 4
        if self.v[x] != self.v[y]:
            self.pc += 2
            if self.memory[self.pc - 2] == 0xF0 and self.memory[self.pc - 1] == 0x00:
                self.pc += 2
        self.last_op = f"SKNE V{x:01X}, V{y:01X} (comparing {self.v[x]:02X} to {self.v[y]:02X})"

    def load_index_reg_with_value(self):
        """
        Annn - LOAD I, nnn

        Load index register with constant value. The calculation for the
        constant value is performed on the operand:

           Bits:  15-12     11-8      7-4       3-0
                    A         n        n         n
        """
        self.index = self.operand & 0x0FFF
        self.last_op = f"LOAD I, {self.index:03X}"

    def jump_to_register_plus_value(self):
        """
        Bnnn - JUMP [V0 + nnn] | [Vx + nn]

        Load the program counter with the memory value located in the specified
        operand plus the value of the V0 register. The address calculation
        is based on the operand, masked as follows:

           Bits:  15-12     11-8      7-4       3-0
                    B         n        n         n

        Note that a quirk exists with several emulators. With some Super Chip 8
        emulators, bits 11-8 are interpreted to be a register to use as the
        base offset, so the address calculation and register source would be:

           Bits:  15-12     11-8      7-4       3-0
                    B         x        n         n
        """
        if self.jump_quirks:
            x = (self.operand & 0x0F00) >> 8
            self.pc = self.v[x] + (self.operand & 0x00FF)
            self.last_op = f"JUMP V{x:01X} + {self.operand & 0x0FF:03X}"
        else:
            self.pc = self.v[0] + (self.operand & 0x0FFF)
            self.last_op = f"JUMP V0 + {self.operand & 0x0FFF:03X}"

    def generate_random_number(self):
        """
        Cxnn - RAND Vx, nn

        A random number between 0 and 255 is generated. The contents of it are
        then ANDed with the constant value passed in the operand. The result is
        stored in the x register. The register and constant values are
        calculated as follows:

           Bits:  15-12     11-8      7-4       3-0
                    C         x        n         n
        """
        value = self.operand & 0x00FF
        x = (self.operand & 0x0F00) >> 8
        self.v[x] = value & randint(0, 255)
        self.last_op = f"RAND V{x:01X}, {value:02X}"

    def draw_sprite(self):
        """
        Dxyn - DRAW x, y, num_bytes

        Draws the sprite pointed to in the index register at the specified
        x and y coordinates. Drawing is done via an XOR routine, meaning that
        if the target pixel is already turned on, and a pixel is set to be
        turned on at that same location via the draw, then the pixel is turned
        off. The routine will wrap the pixels if they are drawn off the edge
        of the screen. Each sprite is 8 bits (1 byte) wide. The num_bytes
        parameter sets how tall the sprite is. Consecutive bytes in the memory
        pointed to by the index register make up the bytes of the sprite. Each
        bit in the sprite byte determines whether a pixel is turned on (1) or
        turned off (0). For example, assume that the index register pointed
        to the following 7 bytes:

                       bit 0 1 2 3 4 5 6 7

           byte 0          0 1 1 1 1 1 0 0
           byte 1          0 1 0 0 0 0 0 0
           byte 2          0 1 0 0 0 0 0 0
           byte 3          0 1 1 1 1 1 0 0
           byte 4          0 1 0 0 0 0 0 0
           byte 5          0 1 0 0 0 0 0 0
           byte 6          0 1 1 1 1 1 0 0

        This would draw a character on the screen that looks like an 'E'. The
        x_source and y_source tell which registers contain the x and y
        coordinates for the sprite. If writing a pixel to a location causes
        that pixel to be turned off, then VF will be set to 1.

           Bits:  15-12     11-8      7-4       3-0
                  unused    x_source  y_source  num_bytes
        """
        x_source = (self.operand & 0x0F00) >> 8
        y_source = (self.operand & 0x00F0) >> 4
        x_pos = self.v[x_source]
        y_pos = self.v[y_source]
        num_bytes = self.operand & 0x000F
        self.v[0xF] = 0

        if num_bytes == 0:
            if self.bitplane == 3:
                self.draw_extended(x_pos, y_pos, 1, index=self.index)
                self.draw_extended(x_pos, y_pos, 2, index=self.index + 32)
            else:
                self.draw_extended(x_pos, y_pos, self.bitplane)
            self.last_op = f"DRAWEX V{x_source:01X}, V{y_source:01X}"
        else:
            if self.bitplane == 3:
                self.draw_normal(x_pos, y_pos, num_bytes, 1, index=self.index)
                self.draw_normal(x_pos, y_pos, num_bytes, 2, index=self.index + num_bytes)
            else:
                self.draw_normal(x_pos, y_pos, num_bytes, self.bitplane)
            self.last_op = f"DRAW V{x_source:01X}, V{y_source:01X}"

    def draw_normal(self, x_pos, y_pos, num_bytes, bitplane, index=None):
        """
        Draws a sprite on the screen while in NORMAL mode.
        
        :param x_pos: the X position of the sprite
        :param y_pos: the Y position of the sprite
        :param num_bytes: the number of bytes to draw
        :param bitplane: the bitplane to draw to
        :param index: the memory index in memory where byte the pattern is stored
        """
        if not index:
            index = self.index

        for y_index in range(num_bytes):
            color_byte = self.memory[index + y_index]
            y_coord = y_pos + y_index
            if not self.clip_quirks or (self.clip_quirks and y_coord < self.screen.get_height()):
                y_coord = y_coord % self.screen.get_height()
                mask = 0x80
                for x_index in range(8):
                    x_coord = x_pos + x_index
                    if not self.clip_quirks or (self.clip_quirks and x_coord < self.screen.get_width()):
                        x_coord = x_coord % self.screen.get_width()
                        turned_on = (color_byte & mask) > 0
                        current_on = self.screen.get_pixel(x_coord, y_coord, bitplane)
                        self.v[0xF] |= 1 if turned_on and current_on else 0
                        self.screen.draw_pixel(x_coord, y_coord, turned_on ^ current_on, bitplane)
                        mask = mask >> 1
        self.screen.update()

    def draw_extended(self, x_pos, y_pos, bitplane, index=None):
        """
        Draws a sprite on the screen while in EXTENDED mode. Sprites in this
        mode are assumed to be 16x16 pixels. This means that two bytes will
        be read from the memory location, and 16 two-byte sequences in total
        will be read.

        :param x_pos: the X position of the sprite
        :param y_pos: the Y position of the sprite
        :param bitplane: the bitplane to draw to
        :param index: the memory index in memory where byte the pattern is stored
        """
        if not index:
            index = self.index

        for y_index in range(16):
            for x_byte in range(2):
                color_byte = self.memory[index + (y_index * 2) + x_byte]
                y_coord = y_pos + y_index
                if y_coord < self.screen.get_height():
                    y_coord = y_coord % self.screen.get_height()
                    mask = 0x80
                    for x_index in range(8):
                        x_coord = x_pos + x_index + (x_byte * 8)
                        if not self.clip_quirks or (self.clip_quirks and x_coord < self.screen.get_width()):
                            x_coord = x_coord % self.screen.get_width()
                            turned_on = (color_byte & mask) > 0
                            current_on = self.screen.get_pixel(x_coord, y_coord, bitplane)
                            self.v[0xF] += 1 if turned_on and current_on else 0
                            self.screen.draw_pixel(x_coord, y_coord, turned_on ^ current_on, bitplane)
                            mask = mask >> 1
                else:
                    self.v[0xF] += 1
        self.screen.update()

    def index_load_long(self):
        """
        F000 - LOADLONG

        Loads the index register with a 16-bit long value. Consumes the next two
        bytes from memory and increments the PC by two bytes.
        """
        self.index = (self.memory[self.pc] << 8) + self.memory[self.pc+1]
        self.pc += 2
        self.last_op = f"LOADLONG {self.index:04X}"

    def set_bitplane(self):
        """
        Fn01 - BITPLANE n

        Selects the active bitplane for screen drawing operations. Bitplane
        selection is as follows:

          0 - no bitplane selected
          1 - first bitplane selected
          2 - second bitplane selected
          3 - first and second bitplane selected

        The bitplane selection values is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         n        0         1
        """
        self.bitplane = (self.operand & 0x0F00) >> 8
        self.last_op = f"BITPLANE {self.bitplane:01X}"

    def load_audio_pattern_buffer(self):
        """
        F002 - AUDIO

        Loads the 16-byte audio pattern buffer with 16 bytes from memory
        pointed to by the index register.
        """
        for x in range(16):
            self.audio_pattern_buffer[x] = self.memory[self.index + x]
        self.calculate_audio_waveform()
        self.last_op = f"AUDIO {self.index:04X}"

    def move_delay_timer_into_reg(self):
        """
        Fx07 - LOAD Vx, DELAY

        Move the value of the delay timer into the x register. The
        register calculation is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         x        0         7
        """
        x = (self.operand & 0x0F00) >> 8
        self.v[x] = self.delay
        self.last_op = f"LOAD V{x:01X}, DELAY"

    def wait_for_keypress(self):
        """
        Fx0A - KEYD Vx

        Stop execution until a key is pressed. The main emulator loop is responsible
        for checking for keypress events and passing them into the function
        decode_keypress_and_continue to continue the exectuion loop. The register calculation is
        as follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         x        0         A
        """
        x = (self.operand & 0x0F00) >> 8
        self.awaiting_keypress = True
        self.keypress_register = x
        self.last_op = f"KEYD V{x:01X}"

    def decode_keypress_and_continue(self, keys_pressed):
        """
        Given a set of keys pressed, checks to see if any of them are chip8
        keys, and if they are, store them in the register specified by the
        wait_for_keypress function. Will flag the CPU to continue executing.

        :param keys_pressed: the list of keys pressed
        """
        for keyval, lookup_key in KEY_MAPPINGS.items():
            if keys_pressed[lookup_key]:
                self.v[self.keypress_register] = keyval
                self.awaiting_keypress = False

    def move_reg_into_delay_timer(self):
        """
        Fx15 - LOAD DELAY, Vx

        Move the value stored in the specified x register into the delay
        timer. The register calculation is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         x        1         5
        """
        x = (self.operand & 0x0F00) >> 8
        self.delay = self.v[x]
        self.last_op = f"LOAD DELAY, V{x:01X}"

    def move_reg_into_sound_timer(self):
        """
        Fx18 - LOAD SOUND, Vx

        Move the value stored in the specified x register into the sound
        timer. The register calculation is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         x        1         8
        """
        x = (self.operand & 0x0F00) >> 8
        self.sound = self.v[x]
        self.last_op = f"LOAD SOUND, V{x:01X}"

    def load_index_with_reg_sprite(self):
        """
        Fx29 - LOAD I, Vx

        Load the index with the sprite indicated in the x register. All
        sprites are 5 bytes long, so the location of the specified sprite
        is its index multiplied by 5. The register calculation is as
        follows:

           Bits:  15-12     11-8      7-4       3-0
                    F        x         2         9
        """
        x = (self.operand & 0x0F00) >> 8
        self.index = self.v[x] * 5
        self.last_op = f"LOAD I, V{x:01X}"

    def load_index_with_extended_reg_sprite(self):
        """
        Fx30 - LOAD I, Vx

        Load the index with the sprite indicated in the x register. All
        sprites are 10 bytes long, so the location of the specified sprite
        is its index multiplied by 10. The register calculation is as
        follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         x        2         9
        """
        x = (self.operand & 0x0F00) >> 8
        self.index = self.v[x] * 10
        self.last_op = f"LOADEXT I, V{x:01X}"

    def add_reg_into_index(self):
        """
        Fx1E - ADD  I, Vx

        Add the value of the x register into the index register value. The
        register calculation is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         x        1         E
        """
        x = (self.operand & 0x0F00) >> 8
        self.index += self.v[x]
        self.last_op = f"ADD I, V{x:01X}"

    def store_bcd_in_memory(self):
        """
        Fx33 - BCD

        Take the value stored in source and place the digits in the following
        locations:

            hundreds   -> self.memory[index]
            tens       -> self.memory[index + 1]
            ones       -> self.memory[index + 2]

        For example, if the value is 123, then the following values will be
        placed at the specified locations:

             1 -> self.memory[index]
             2 -> self.memory[index + 1]
             3 -> self.memory[index + 2]

        The register calculation is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         x        3         3
        """
        x = (self.operand & 0x0F00) >> 8
        bcd_value = f"{self.v[x]:03d}"
        self.memory[self.index] = int(bcd_value[0])
        self.memory[self.index + 1] = int(bcd_value[1])
        self.memory[self.index + 2] = int(bcd_value[2])
        self.last_op = f"BCD V{x:01X} ({bcd_value})"

    def load_pitch(self):
        """
        Fx3A - PITCH Vx

        Loads the value from register x into the pitch register. The
        register calculation is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         x        3         A
        """
        x = (self.operand & 0x0F00) >> 8
        self.pitch = self.v[x]
        self.playback_rate = 4000 * 2 ** ((self.pitch - 64) / 48)
        self.last_op = f"PITCH V{x:01X}"

    def store_regs_in_memory(self):
        """
        Fn55 - STOR [I]

        Store all V registers in the memory pointed to by the index
        register. The register calculation is as follows:

           Bits:  15-12     11-8      7-4       3-0
                    F         n        5         5

        For example, to store all V registers, num_regs would contain
        the value 'F'.
        """
        num_regs = (self.operand & 0x0F00) >> 8
        for counter in range(num_regs + 1):
            self.memory[self.index + counter] = self.v[counter]
        if not self.index_quirks:
            self.index += num_regs + 1
        self.last_op = f"STOR {num_regs:01X}"

    def read_regs_from_memory(self):
        """
        Fn65 - LOAD V, I

        Read the V registers from the memory pointed to by the index
        register. The number of registers to read back is encoded
        as the numeric value in the instruction

           Bits:  15-12     11-8      7-4       3-0
                    F         n        6         5

        For example, to load all the V registers, num_regs would
        contain the value 'F'.
        """
        num_regs = (self.operand & 0x0F00) >> 8
        for counter in range(num_regs + 1):
            self.v[counter] = self.memory[self.index + counter]
        if not self.index_quirks:
            self.index += num_regs + 1
        self.last_op = f"READ {num_regs}"

    def store_regs_in_rpl(self):
        """
        Fs75 - SRPL Vs

        Stores all or fewer of the V registers in the RPL store.

           Bits:  15-12     11-8      7-4       3-0
                  unused    num_regs   7         5

        For example, to store all the V registers, num_regs would contain
        the value 'F'.
        """
        num_regs = (self.operand & 0x0F00) >> 8
        for counter in range(num_regs + 1):
            self.rpl[counter] = self.v[counter]
        self.last_op = f"STORRPL {num_regs:01X}"

    def read_regs_from_rpl(self):
        """
        Fs85 - LRPL Vs

        Read all or fewer of the V registers from the RPL store.

           Bits:  15-12     11-8      7-4       3-0
                  unused    num_regs   6         5

        For example, to load all the V registers, num_regs would
        contain the value 'F'.
        """
        num_regs = (self.operand & 0x0F00) >> 8
        for counter in range(num_regs + 1):
            self.v[counter] = self.rpl[counter]
        self.last_op = f"READRPL {num_regs:01X}"

    def reset(self):
        """
        Reset the CPU by blanking out all registers, and reseting the stack
        pointer and program counter to their starting values.
        """
        self.last_op = "None"
        self.sound = 0
        self.delay = 0
        self.v = [0] * NUM_REGISTERS
        self.pc = PROGRAM_COUNTER_START
        self.sp = STACK_POINTER_START
        self.index = 0
        self.rpl = [0] * NUM_REGISTERS
        self.pitch = 64
        self.playback_rate = 4000
        self.audio_pattern_buffer = [0] * 16
        self.sound_playing = False
        self.sound_waveform = None
        self.bitplane = 1

    def load_rom(self, filename, offset=PROGRAM_COUNTER_START):
        """
        Load the ROM indicated by the filename into memory.

        :param filename: the name of the file to load
        :type filename: string

        :param offset: the location in memory at which to load the ROM
        :type offset: integer
        """
        with open(filename, 'rb') as rom_file:
            rom_data = rom_file.read()
            for index, val in enumerate(rom_data):
                self.memory[offset + index] = val

    def decrement_timers(self):
        """
        Decrement both the sound and delay timer.
        """
        self.delay -= 1 if self.delay > 0 else 0
        self.sound -= 1 if self.delay > 0 else 0
        if self.sound > 0 and not self.sound_playing:
            if self.sound_waveform:
                self.sound_waveform.play(loops=-1)
            self.sound_playing = True

        if self.sound == 0 and self.sound_playing:
            if self.sound_waveform:
                self.sound_waveform.stop()
            self.sound_playing = False

    def calculate_audio_waveform(self):
        """
        Based on a playback rate specified by the XO Chip pitch, generate
        an audio waveform from the 16-byte audio_pattern_buffer. It converts
        the 16-bytes pattern into 128 separate bits. The bits are then used to fill
        a sample buffer. The sample buffer is filled by resampling the 128-bit
        pattern at the specified frequency. The sample buffer is then repeated
        until it is at least MIN_AUDIO_SAMPLES long. Playback (if currently
        happening) is stopped, the new waveform is loaded, and then playback
        is starts again (if the emulator had previously been playing a sound).
        """
        # Convert the 16-byte value into an array of 128-bit samples
        data = [int(bit) * 255 for bit in ''.join(f"{audio_byte:08b}" for audio_byte in self.audio_pattern_buffer)]
        step = self.playback_rate / PYGAME_AUDIO_PLAYBACK_RATE
        buffer = []

        # Generate the initial re-sampled buffer
        position = 0.0
        while position < 128:
            buffer.append(data[int(position)])
            position += step

        # Lengthen the buffer until it is at least MIN_AUDIO_SAMPLES long
        while len(buffer) < MIN_AUDIO_SAMPLES:
            buffer += buffer

        # Stop playing any waveform if it is currently playing
        if self.sound_playing and self.sound_waveform:
            self.sound_waveform.stop()

        # Generate a new waveform from the sample buffer
        self.sound_waveform = Sound(np.array(buffer).astype(np.uint8))

        # Start playing the sound again if we should be playing one
        if self.sound_playing:
            self.sound_waveform.play(loops=-1)

# E N D   O F   F I L E ########################################################

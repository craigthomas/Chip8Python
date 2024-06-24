"""
Copyright (C) 2024 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A simple Chip 8 emulator - see the README file for more information.
"""
# I M P O R T S ###############################################################

import mock
import pygame
import unittest

from mock import patch, call

from chip8.cpu import Chip8CPU, UnknownOpCodeException, MODE_EXTENDED
from chip8.screen import Chip8Screen

# C O N S T A N T S ###########################################################

KEYPRESS_TABLE = [0] * 512

# C L A S S E S ###############################################################


class TestChip8CPU(unittest.TestCase):
    """
    A test class for the Chip 8 CPU.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.screen = mock.MagicMock()
        self.cpu = Chip8CPU(self.screen)
        self.cpu_spy = mock.Mock(wraps=self.cpu)

    def test_clear_return_with_unknown_opcode(self):
        with self.assertRaises(UnknownOpCodeException) as context:
            self.cpu.execute_instruction(operand=0x00FA)
        self.assertEqual("Unknown op-code: 00FA", str(context.exception))

    def test_bitplane_1_init(self):
        self.assertEqual(1, self.cpu.bitplane)

    def test_set_bitplane(self):
        self.cpu.operand = 0xF201
        self.cpu.set_bitplane()
        self.assertEqual(2, self.cpu.bitplane)

    def test_set_bitplane_integration(self):
        self.cpu.memory[0x0200] = 0xF2
        self.cpu.memory[0x0201] = 0x01
        self.cpu.execute_instruction()
        self.assertEqual(2, self.cpu.bitplane)

    def test_memory_size_default_64k(self):
        self.assertEqual(65536, len(self.cpu.memory))

    def test_pitch_init_64(self):
        self.assertEqual(64, self.cpu.pitch)
        self.assertEqual(4000, self.cpu.playback_rate)

    def test_load_pitch(self):
        self.cpu.v[1] = 112
        self.cpu.operand = 0xF13A
        self.cpu.load_pitch()
        self.assertEqual(112, self.cpu.pitch)
        self.assertEqual(8000, self.cpu.playback_rate)

    def test_load_pitch_integration(self):
        self.cpu.v[1] = 112
        self.cpu.memory[0x0200] = 0xF1
        self.cpu.memory[0x0201] = 0x3A
        self.cpu.execute_instruction()
        self.assertEqual(112, self.cpu.pitch)
        self.assertEqual(8000, self.cpu.playback_rate)

    def test_return_from_subroutine(self):
        for address in range(0x200, 0xFFFF, 0x10):
            self.cpu.memory[self.cpu.sp] = address & 0x00FF
            self.cpu.memory[self.cpu.sp + 1] = \
                (address & 0xFF00) >> 8
            self.cpu.sp += 2
            self.cpu.pc = 0
            self.cpu.return_from_subroutine()
            self.assertEqual(self.cpu.pc, address)

    def test_jump_to_address(self):
        for address in range(0, 0xFFFF, 0x10):
            self.cpu.operand = address
            self.cpu.pc = 0
            self.assertEqual(self.cpu.pc, 0)
            self.cpu.jump_to_address()
            self.assertEqual(self.cpu.pc, (address & 0x0FFF))

    def test_jump_to_subroutine(self):
        for address in range(0x200, 0xFFFF, 0x10):
            self.cpu.operand = address
            self.cpu.sp = 0
            self.cpu.pc = 0x100
            self.cpu.jump_to_subroutine()
            self.assertEqual(self.cpu.pc, (address & 0x0FFF))
            self.assertEqual(self.cpu.sp, 2)
            self.assertEqual(self.cpu.memory[0], 0)
            self.assertEqual(self.cpu.memory[1], 0x1)

    def test_skip_if_reg_equal_value(self):
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                for reg_value in range(0, 0xFF, 0x10):
                    self.cpu.operand = register << 8
                    self.cpu.operand += value
                    self.cpu.v[register] = reg_value
                    self.cpu.pc = 0
                    self.assertEqual(self.cpu.pc, 0)
                    self.cpu.skip_if_reg_equal_val()
                    if value == reg_value:
                        self.assertEqual(self.cpu.pc, 2)
                    else:
                        self.assertEqual(self.cpu.pc, 0)

    def test_skip_if_reg_not_equal_val(self):
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                for reg_value in range(0, 0xFF, 0x10):
                    self.cpu.operand = register << 8
                    self.cpu.operand += value
                    self.cpu.v[register] = reg_value
                    self.cpu.pc = 0
                    self.cpu.skip_if_reg_not_equal_val()
                    if value != reg_value:
                        self.assertEqual(self.cpu.pc, 2)
                    else:
                        self.assertEqual(self.cpu.pc, 0)

    def test_skip_if_reg_equal_reg(self):
        for reg_num in range(0x10):
            self.cpu.v[reg_num] = reg_num

        for reg_1 in range(0x10):
            for reg_2 in range(0x10):
                self.cpu.operand = reg_1
                self.cpu.operand <<= 4
                self.cpu.operand += reg_2
                self.cpu.operand <<= 4

                self.cpu.pc = 0
                self.assertEqual(self.cpu.pc, 0)
                self.cpu.skip_if_reg_equal_reg()

                # If we are testing the same register as the source and the
                # destination, then a skip WILL occur
                if reg_1 == reg_2:
                    self.assertEqual(self.cpu.pc, 2)
                else:
                    self.assertEqual(self.cpu.pc, 0)

    def test_move_value_to_reg(self):
        val = 0x23
        for reg_num in range(0x10):
            self.assertEqual(self.cpu.v[0x0], 0)

        for reg_num in range(0x10):
            self.cpu.operand = 0x60 + reg_num
            self.cpu.operand <<= 8
            self.cpu.operand += val

            self.cpu.move_value_to_reg()

            for reg_to_check in range(0x10):
                if reg_to_check != reg_num:
                    self.assertEqual(self.cpu.v[reg_to_check], 0)
                else:
                    self.assertEqual(self.cpu.v[reg_to_check], val)

            self.cpu.v[reg_num] = 0

    def test_add_value_to_reg(self):
        for register in range(0x10):
            for reg_value in range(0, 0xFF, 0x10):
                for value in range(0, 0xFF, 0x10):
                    self.cpu.v[register] = reg_value
                    self.cpu.operand = register << 8
                    self.cpu.operand += value
                    self.assertEqual(
                        self.cpu.v[register],
                        reg_value)
                    self.cpu.add_value_to_reg()
                    if value + reg_value < 256:
                        self.assertEqual(
                            self.cpu.v[register],
                            value + reg_value)
                    else:
                        self.assertEqual(
                            self.cpu.v[register],
                            (value + reg_value - 256))

    def test_move_reg_into_reg(self):
        for source in range(0x10):
            for target in range(0x10):
                if source != target:
                    self.cpu.v[target] = 0x32
                    self.cpu.v[source] = 0
                    self.cpu.operand = source << 8
                    self.cpu.operand += (target << 4)
                    self.cpu.move_reg_into_reg()
                    self.assertEqual(self.cpu.v[source], 0x32)

    def test_logical_or(self):
        for source in range(0x10):
            for target in range(0x10):
                if source != target:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0, 0xFF, 0x10):
                            self.cpu.v[source] = source_val
                            self.cpu.v[target] = target_val
                            self.cpu.operand = source << 8
                            self.cpu.operand += (target << 4)
                            self.cpu.logical_or()
                            self.assertEqual(
                                self.cpu.v[source],
                                source_val | target_val)
                else:
                    for source_val in range(0, 0xFF, 0x10):
                        self.cpu.v[source] = source_val
                        self.cpu.operand = source << 8
                        self.cpu.operand += (target << 4)
                        self.cpu.logical_or()
                        self.assertEqual(
                            self.cpu.v[source],
                            source_val)

    def test_logical_and(self):
        for source in range(0x10):
            for target in range(0x10):
                if source != target:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0, 0xFF, 0x10):
                            self.cpu.v[source] = source_val
                            self.cpu.v[target] = target_val
                            self.cpu.operand = source << 8
                            self.cpu.operand += (target << 4)
                            self.cpu.logical_and()
                            self.assertEqual(
                                self.cpu.v[source],
                                source_val & target_val)
                else:
                    for source_val in range(256):
                        self.cpu.v[source] = source_val
                        self.cpu.operand = source << 8
                        self.cpu.operand += (target << 4)
                        self.cpu.logical_and()
                        self.assertEqual(
                            self.cpu.v[source],
                            source_val)

    def test_exclusive_or(self):
        for source in range(0x10):
            for target in range(0x10):
                if source != target:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0xF):
                            self.cpu.v[source] = source_val
                            self.cpu.v[target] = target_val
                            self.cpu.operand = source << 8
                            self.cpu.operand += (target << 4)
                            self.cpu.exclusive_or()
                            self.assertEqual(
                                self.cpu.v[source],
                                source_val ^ target_val)

    def test_add_to_reg(self):
        for source in range(0xF):
            for target in range(0xF):
                if source != target:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0, 0xFF, 0x10):
                            self.cpu.v[source] = source_val
                            self.cpu.v[target] = target_val
                            self.cpu.operand = source << 8
                            self.cpu.operand += (target << 4)
                            self.cpu.add_reg_to_reg()
                            if source_val + target_val > 255:
                                self.assertEqual(
                                    self.cpu.v[source],
                                    source_val + target_val - 256)
                                self.assertEqual(
                                    self.cpu.v[0xF], 1)
                            else:
                                self.assertEqual(
                                    self.cpu.v[source],
                                    source_val + target_val)
                                self.assertEqual(
                                    self.cpu.v[0xF], 0)

    def test_subtract_reg_from_reg(self):
        for source in range(0xF):
            for target in range(0xF):
                if source != target:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0xF):
                            self.cpu.v[source] = source_val
                            self.cpu.v[target] = target_val
                            self.cpu.operand = source << 8
                            self.cpu.operand += (target << 4)
                            self.cpu.subtract_reg_from_reg()
                            if source_val > target_val:
                                self.assertEqual(self.cpu.v[source], source_val - target_val)
                                self.assertEqual(
                                    self.cpu.v[0xF], 1)
                            elif source_val == target_val:
                                self.assertEqual(self.cpu.v[source], 0)
                                self.assertEqual(self.cpu.v[0xF], 1)
                            else:
                                self.assertEqual(self.cpu.v[source], 256 + source_val - target_val)
                                self.assertEqual(self.cpu.v[0xF], 0)

    def test_right_shift_reg_quirks(self):
        self.cpu.shift_quirks = True
        for register in range(0xF):
            for value in range(0, 0xFF, 0x10):
                self.cpu.v[register] = value
                self.cpu.operand = register << 8
                for index in range(1, 8):
                    shifted_val = value >> index
                    self.cpu.v[0xF] = 0
                    bit_zero = self.cpu.v[register] & 0x1
                    self.cpu.right_shift_reg()
                    self.assertEqual(self.cpu.v[register], shifted_val)
                    self.assertEqual(self.cpu.v[0xF], bit_zero)

    def test_right_shift_reg(self):
        self.cpu.shift_quirks = False
        for x in range(0xF):
            for y in range(0xF):
                for value in range(0, 0xFF, 0x10):
                    self.cpu.operand = x << 8
                    self.cpu.operand |= y << 4
                    self.cpu.v[y] = value
                    shifted_val = value >> 1
                    self.cpu.v[0xF] = 0
                    bit_zero = self.cpu.v[y] & 0x1
                    self.cpu.right_shift_reg()
                    self.assertEqual(self.cpu.v[x], shifted_val)
                    self.assertEqual(self.cpu.v[0xF], bit_zero)

    def test_subtract_reg_from_reg1(self):
        for x in range(0xF):
            for y in range(0xF):
                if x != y:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0xF):
                            self.cpu.v[x] = source_val
                            self.cpu.v[y] = target_val
                            self.cpu.operand = x << 8
                            self.cpu.operand += (y << 4)
                            self.cpu.subtract_reg_from_reg1()
                            if target_val > source_val:
                                self.assertEqual(target_val - source_val, self.cpu.v[x])
                                self.assertEqual(1, self.cpu.v[0xF])
                            elif target_val == source_val:
                                self.assertEqual(0, self.cpu.v[x])
                                self.assertEqual(1, self.cpu.v[0xF])
                            else:
                                self.assertEqual(256 + target_val - source_val, self.cpu.v[x])
                                self.assertEqual(0, self.cpu.v[0xF])

    def test_left_shift_reg(self):
        self.cpu.shift_quirks = False
        for x in range(0xF):
            for y in range(0xF):
                for value in range(256):
                    self.cpu.v[y] = value
                    self.cpu.operand = x << 8
                    self.cpu.operand |= y << 4
                    bit_seven = (value & 0x80) >> 8
                    shifted_val = (value << 1) & 0xFF
                    self.cpu.v[0xF] = 0
                    self.cpu.left_shift_reg()
                    self.assertEqual(shifted_val, self.cpu.v[x])
                    self.assertEqual(bit_seven, self.cpu.v[0xF])

    def test_left_shift_reg_quirks(self):
        self.cpu.shift_quirks = True
        for x in range(0xF):
            for value in range(256):
                self.cpu.v[x] = value
                self.cpu.operand = x << 8
                shifted_val = value
                for index in range(1, 8):
                    bit_seven = (shifted_val & 0x80) >> 8
                    shifted_val = (value << index) & 0xFF
                    self.cpu.v[0xF] = 0
                    self.cpu.left_shift_reg()
                    self.assertEqual(shifted_val, self.cpu.v[x])
                    self.assertEqual(bit_seven, self.cpu.v[0xF])

    def test_skip_if_reg_not_equal_reg(self):
        for register in range(0x10):
            self.cpu.v[register] = register

        for source in range(0x10):
            for target in range(0x10):
                self.cpu.operand = source << 8
                self.cpu.operand += (target << 4)
                self.cpu.pc = 0
                self.cpu.skip_if_reg_not_equal_reg()
                if source != target:
                    self.assertEqual(self.cpu.pc, 2)
                else:
                    self.assertEqual(self.cpu.pc, 0)

    def test_load_index_reg_with_value(self):
        for value in range(0x10000):
            self.cpu.operand = value
            self.cpu.load_index_reg_with_value()
            self.assertEqual(self.cpu.index, value & 0x0FFF)

    def test_jump_to_index_plus_value(self):
        for index in range(0, 0xFFF, 0x10):
            for value in range(0, 0xFFF, 0x10):
                self.cpu.v[0] = index
                self.cpu.pc = 0
                self.cpu.operand = value
                self.cpu.jump_to_register_plus_value()
                self.assertEqual(index + value, self.cpu.pc)

    def test_jump_to_index_plus_value_quirks(self):
        self.cpu.jump_quirks = True
        for register in range(0, 0xF):
            for index in range(0, 0xFFF, 0x10):
                for value in range(0, 0xFF, 0x10):
                    self.cpu.v[register] = index
                    self.cpu.pc = 0
                    self.cpu.operand = value
                    self.cpu.operand |= (register << 8)
                    self.cpu.jump_to_register_plus_value()
                    self.assertEqual(index + value, self.cpu.pc)

    def test_generate_random_number(self):
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                self.cpu.v[register] = -1
                self.cpu.operand = register << 8
                self.cpu.operand += value
                self.cpu.generate_random_number()
                self.assertTrue(self.cpu.v[register] >= 0)
                self.assertTrue(self.cpu.v[register] <= 255)

    def test_move_delay_timer_into_reg(self):
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                self.cpu.delay = value
                self.cpu.operand = register << 8
                self.cpu.v[register] = 0
                self.cpu.move_delay_timer_into_reg()
                self.assertEqual(self.cpu.v[register], value)

    def test_move_reg_into_delay_timer(self):
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                self.cpu.v[register] = value
                self.cpu.operand = register << 8
                self.cpu.delay = 0
                self.cpu.move_reg_into_delay_timer()
                self.assertEqual(self.cpu.delay, value)

    def test_move_reg_into_sound_timer(self):
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                self.cpu.v[register] = value
                self.cpu.operand = register << 8
                self.cpu.sound = 0
                self.cpu.move_reg_into_sound_timer()
                self.assertEqual(self.cpu.sound, value)

    def test_add_reg_into_index(self):
        for register in range(0x10):
            for index in range(0, 0xFFF, 0x10):
                self.cpu.index = index
                self.cpu.v[register] = 0x89
                self.cpu.operand = (register << 8)
                self.cpu.add_reg_into_index()
                self.assertEqual(index + 0x89, self.cpu.index)

    def test_load_index_with_reg_sprite(self):
        for number in range(0x10):
            self.cpu.index = 0xFFF
            self.cpu.v[0] = number
            self.cpu.operand = 0xF029
            self.cpu.load_index_with_reg_sprite()
            self.assertEqual(number * 5, self.cpu.index)

    def test_store_bcd_in_memory(self):
        for number in range(0x100):
            number_as_string = '{:03d}'.format(number)
            self.cpu.index = 0
            self.cpu.v[0] = number
            self.cpu.operand = 0xF033
            self.cpu.store_bcd_in_memory()
            self.assertEqual(int(number_as_string[0]), self.cpu.memory[0])
            self.assertEqual(int(number_as_string[1]), self.cpu.memory[1])
            self.assertEqual(int(number_as_string[2]), self.cpu.memory[2])

    def test_store_regs_in_memory(self):
        index = 0x500
        self.cpu.index = index

        for x in range(0x10):
            self.cpu.v[x] = x + 0x89

        for num_regs in range(0x10):
            self.cpu.index = index

            for counter in range(0x10):
                self.cpu.memory[self.cpu.index + counter] = 0x00

            self.cpu.operand = (num_regs << 8)
            index_before = self.cpu.index
            self.cpu.store_regs_in_memory()
            self.assertEqual(self.cpu.index, index_before + num_regs + 1)

            for counter in range(0x10):
                if counter > num_regs:
                    self.assertEqual(self.cpu.memory[index + counter], 0x00)
                else:
                    self.assertEqual(self.cpu.memory[index + counter], 0x89 + counter)

    def test_store_regs_in_memory_index_quirks(self):
        self.cpu.index_quirks = True
        index = 0x500
        self.cpu.index = index

        for x in range(0x10):
            self.cpu.v[x] = x + 0x89

        for num_regs in range(0x10):
            self.cpu.index = index

            for counter in range(0x10):
                self.cpu.memory[self.cpu.index + counter] = 0x00

            self.cpu.operand = (num_regs << 8)
            index_before = self.cpu.index
            self.cpu.store_regs_in_memory()
            self.assertEqual(self.cpu.index, index_before)

            for counter in range(0x10):
                if counter > num_regs:
                    self.assertEqual(self.cpu.memory[index + counter], 0x00)
                else:
                    self.assertEqual(self.cpu.memory[index + counter], 0x89 + counter)

    def test_read_regs_from_memory(self):
        index = 0x500
        self.cpu.index = index

        for num_regs in range(0x10):
            self.cpu.memory[index + num_regs] = num_regs + 0x89

        for num_regs in range(0x10):
            self.cpu.index = index
            for reg_to_set in range(0x10):
                self.cpu.v[reg_to_set] = 0

            self.cpu.operand = 0xF065
            self.cpu.operand |= (num_regs << 8)
            index_before = self.cpu.index
            self.cpu.read_regs_from_memory()
            self.assertEqual(self.cpu.index, index_before + num_regs + 1)

            for reg_to_check in range(0x10):
                if reg_to_check > num_regs:
                    self.assertEqual(self.cpu.v[reg_to_check], 0)
                else:
                    self.assertEqual(self.cpu.v[reg_to_check], reg_to_check + 0x89)

    def test_read_regs_from_memory_index_quirks(self):
        self.cpu.index_quirks = True
        index = 0x500
        self.cpu.index = index

        for register in range(0x10):
            self.cpu.memory[index + register] = register + 0x89

        for register in range(0x10):
            self.cpu.index = index
            for reg_to_set in range(0x10):
                self.cpu.v[reg_to_set] = 0

            self.cpu.operand = 0xF065
            self.cpu.operand |= (register << 8)
            index_before = self.cpu.index
            self.cpu.read_regs_from_memory()
            self.assertEqual(self.cpu.index, index_before)

            for reg_to_check in range(0x10):
                if reg_to_check > register:
                    self.assertEqual(self.cpu.v[reg_to_check], 0)
                else:
                    self.assertEqual(self.cpu.v[reg_to_check], reg_to_check + 0x89)

    def test_store_regs_in_rpl(self):
        for register in range(0x10):
            self.cpu.v[register] = register
            self.cpu.operand = (register << 8)
            self.cpu.store_regs_in_rpl()
            for counter in range(register):
                self.assertEqual(counter, self.cpu.rpl[counter])

    def test_read_regs_from_rpl(self):
        for register in range(0xF):
            self.cpu.rpl[register] = register + 0x89

        for register in range(0xF):
            for reg_to_set in range(0xF):
                self.cpu.v[reg_to_set] = 0

            self.cpu.operand = 0xF000
            self.cpu.operand += (register << 8)
            self.cpu.operand += 0x85
            self.cpu.read_regs_from_rpl()
            for reg_to_check in range(0xF):
                if reg_to_check > register:
                    self.assertEqual(self.cpu.v[reg_to_check], 0)
                else:
                    self.assertEqual(
                        self.cpu.v[reg_to_check],
                        reg_to_check + 0x89)

    def test_load_rom(self):
        self.cpu.load_rom('test/romfile', 0)
        self.assertEqual(ord('a'), self.cpu.memory[0])
        self.assertEqual(ord('b'), self.cpu.memory[1])
        self.assertEqual(ord('c'), self.cpu.memory[2])
        self.assertEqual(ord('d'), self.cpu.memory[3])
        self.assertEqual(ord('e'), self.cpu.memory[4])
        self.assertEqual(ord('f'), self.cpu.memory[5])
        self.assertEqual(ord('g'), self.cpu.memory[6])

    def test_decrement_timers_decrements_by_one(self):
        self.cpu.delay = 2
        self.cpu.sound = 2
        self.cpu.decrement_timers()
        self.assertEqual(1, self.cpu.delay)
        self.assertEqual(1, self.cpu.sound)

    def test_decrement_timers_does_not_go_negative(self):
        self.cpu.delay = 0
        self.cpu.sound = 0
        self.cpu.decrement_timers()
        self.assertEqual(0, self.cpu.delay)
        self.assertEqual(0, self.cpu.sound)

    def test_clear_screen(self):
        self.cpu.operand = 0xE0
        self.cpu.clear_return()
        self.screen.clear_screen.assert_called_with()

    def test_clear_return_from_subroutine(self):
        self.cpu.operand = 0xEE
        address = 0x500
        self.cpu.memory[self.cpu.sp] = address & 0x00FF
        self.cpu.memory[self.cpu.sp + 1] = \
            (address & 0xFF00) >> 8
        self.cpu.sp += 2
        self.cpu.pc = 0
        self.cpu.clear_return()
        self.assertEqual(self.cpu.pc, address)

    def test_operation_9E_pc_skips_if_key_pressed(self):
        self.cpu.operand = 0x09E
        self.cpu.v[0] = 1
        self.cpu.pc = 0
        result_table = [False] * 512
        result_table[pygame.K_1] = True
        with mock.patch("pygame.key.get_pressed", return_value=result_table) as key_mock:
            self.cpu.keyboard_routines()
            self.assertTrue(key_mock.asssert_called)
            self.assertEqual(2, self.cpu.pc)

    def test_operation_9E_pc_does_not_skip_if_key_not_pressed(self):
        self.cpu.operand = 0x09E
        self.cpu.v[0] = 1
        self.cpu.pc = 0
        result_table = [False] * 512
        with mock.patch("pygame.key.get_pressed", return_value=result_table) as key_mock:
            self.cpu.keyboard_routines()
            self.assertTrue(key_mock.asssert_called)
            self.assertEqual(0, self.cpu.pc)

    def test_operation_A1_pc_skips_if_key_not_pressed(self):
        self.cpu.operand = 0x0A1
        self.cpu.v[0] = 1
        self.cpu.pc = 0
        result_table = [False] * 512
        with mock.patch("pygame.key.get_pressed", return_value=result_table) as key_mock:
            self.cpu.keyboard_routines()
            self.assertTrue(key_mock.asssert_called)
            self.assertEqual(2, self.cpu.pc)

    def test_operation_A1_pc_does_not_skip_if_key_pressed(self):
        self.cpu.operand = 0x0A1
        self.cpu.v[0] = 1
        self.cpu.pc = 0
        result_table = [False] * 512
        result_table[pygame.K_1] = True
        with mock.patch("pygame.key.get_pressed", return_value=result_table) as key_mock:
            self.cpu.keyboard_routines()
            self.assertTrue(key_mock.asssert_called)
            self.assertEqual(0, self.cpu.pc)

    def test_draw_zero_bytes_vf_not_set(self):
        self.cpu.operand = 0x00
        self.cpu.v[0xF] = 1
        self.screen.get_height.return_value = 64
        self.screen.get_width.return_value = 128
        self.cpu.draw_sprite()
        self.assertTrue(self.screen.update_screen.assert_called)
        self.assertEqual(0, self.cpu.v[0xF])

    def test_execute_instruction_raises_exception_on_unknown_op_code(self):
        with self.assertRaises(UnknownOpCodeException) as context:
            self.cpu.execute_instruction(operand=0x8008)
        self.assertEqual("Unknown op-code: 8008", str(context.exception))

    def test_execute_instruction_raises_exception_on_unknown_op_code_from_cpu(self):
        with self.assertRaises(UnknownOpCodeException) as context:
            self.cpu.operand = 0x8008
            self.cpu.execute_instruction(operand=0x8008)
        self.assertEqual("Unknown op-code: 8008", str(context.exception))

    def test_execute_instruction_on_operand_in_memory(self):
        self.cpu.pc = 0x200
        self.cpu.memory[0x200] = 0x61
        result = self.cpu.execute_instruction()
        self.assertEqual(0x6100, result)
        self.assertEqual(0x202, self.cpu.pc)

    def test_execute_logical_instruction_raises_exception_on_unknown_op_codes(self):
        for x in range(8, 14):
            self.cpu.operand = x
            with self.assertRaises(UnknownOpCodeException):
                self.cpu.execute_logical_instruction()

        # And finally test 15 (F)
        self.cpu.operand = 15
        with self.assertRaises(UnknownOpCodeException):
            self.cpu.execute_logical_instruction()

    def test_misc_routines_raises_exception_on_unknown_op_codes(self):
        self.cpu.operand = 0x0
        with self.assertRaises(UnknownOpCodeException) as context:
            self.cpu.misc_routines()
        self.assertEqual("Unknown op-code: 0000", str(context.exception))

    def test_scroll_down_called(self):
        self.cpu.operand = 0x00C4
        self.cpu.clear_return()
        self.screen.scroll_down.assert_called_with(4)

    def test_scroll_right_called(self):
        self.cpu.operand = 0x00FB
        self.cpu.clear_return()
        self.assertTrue(self.screen.scroll_right.assert_called)

    def test_scroll_left_called(self):
        self.cpu.operand = 0x00FC
        self.cpu.clear_return()
        self.assertTrue(self.screen.scroll_left.assert_called)

    def test_set_extended(self):
        self.cpu.operand = 0x00FF
        self.cpu.clear_return()
        self.assertTrue(self.screen.set_extended.assert_called)
        self.assertEqual("extended", self.cpu.mode)

    def test_disable_extended(self):
        self.cpu.operand = 0x00FE
        self.cpu.clear_return()
        self.assertTrue(self.screen.set_normal.assert_called)
        self.assertEqual("normal", self.cpu.mode)

    def test_exit(self):
        self.cpu.running = True
        self.cpu.operand = 0x00FD
        self.cpu.clear_return()
        self.assertFalse(self.cpu.running)

    def test_draw_extended_called(self):
        self.cpu.mode = MODE_EXTENDED
        self.screen.get_height.return_value = 64
        self.screen.get_width.return_value = 128
        self.cpu.draw_sprite()
        self.assertTrue(self.cpu_spy.draw_extended.assert_called)

    def test_draw_sprite_draws_correct_sprite(self):
        screen = Chip8Screen(2)
        screen.init_display()
        screen_mock = mock.Mock(wraps=screen, spec=screen)
        screen_mock.height = 32
        screen_mock.width = 64
        self.cpu = Chip8CPU(screen_mock)
        self.cpu.memory[0] = 0xAA
        self.cpu.draw_normal(0, 0, 1)
        with patch('chip8.screen.Chip8Screen.draw_pixel'):
            screen_mock.draw_pixel.assert_has_calls([
                call(0, 0, 1),
                call(1, 0, 0),
                call(2, 0, 1),
                call(3, 0, 0),
                call(4, 0, 1),
                call(5, 0, 0),
                call(6, 0, 1),
                call(7, 0, 0)
            ])

    def test_draw_sprite_turns_off_pixels(self):
        screen = Chip8Screen(2)
        screen.init_display()
        screen_mock = mock.Mock(wraps=screen, spec=screen)
        screen_mock.height = 32
        screen_mock.width = 64
        self.cpu = Chip8CPU(screen_mock)
        self.cpu.memory[0] = 0xAA
        self.cpu.draw_normal(0, 0, 1)
        self.cpu.draw_normal(0, 0, 1)
        with patch('chip8.screen.Chip8Screen.draw_pixel'):
            screen_mock.draw_pixel.assert_has_calls([
                call(0, 0, 1),
                call(1, 0, 0),
                call(2, 0, 1),
                call(3, 0, 0),
                call(4, 0, 1),
                call(5, 0, 0),
                call(6, 0, 1),
                call(7, 0, 0),
                call(0, 0, 0),
                call(1, 0, 0),
                call(2, 0, 0),
                call(3, 0, 0),
                call(4, 0, 0),
                call(5, 0, 0),
                call(6, 0, 0),
                call(7, 0, 0)
            ])

    def test_draw_sprite_does_not_turn_off_pixels(self):
        screen = Chip8Screen(2)
        screen.init_display()
        screen_mock = mock.Mock(wraps=screen, spec=screen)
        screen_mock.height = 32
        screen_mock.width = 64
        self.cpu = Chip8CPU(screen_mock)
        self.cpu.memory[0] = 0xAA
        self.cpu.draw_normal(0, 0, 1)
        self.cpu.memory[0] = 0x55
        self.cpu.draw_normal(0, 0, 1)
        with patch('chip8.screen.Chip8Screen.draw_pixel'):
            screen_mock.draw_pixel.assert_has_calls([
                call(0, 0, 1),
                call(1, 0, 0),
                call(2, 0, 1),
                call(3, 0, 0),
                call(4, 0, 1),
                call(5, 0, 0),
                call(6, 0, 1),
                call(7, 0, 0),
                call(0, 0, 1),
                call(1, 0, 1),
                call(2, 0, 1),
                call(3, 0, 1),
                call(4, 0, 1),
                call(5, 0, 1),
                call(6, 0, 1),
                call(7, 0, 1)
            ])

    def test_load_index_with_sprite(self):
        self.cpu.v[1] = 10
        self.cpu.operand = 0xF130
        self.cpu.load_index_with_extended_reg_sprite()
        self.assertEqual(100, self.cpu.index)

    def test_str_function(self):
        self.cpu.v[0] = 0
        self.cpu.v[1] = 1
        self.cpu.v[2] = 2
        self.cpu.v[3] = 3
        self.cpu.v[4] = 4
        self.cpu.v[5] = 5
        self.cpu.v[6] = 6
        self.cpu.v[7] = 7
        self.cpu.v[8] = 8
        self.cpu.v[9] = 9
        self.cpu.v[10] = 10
        self.cpu.v[11] = 11
        self.cpu.v[12] = 12
        self.cpu.v[13] = 13
        self.cpu.v[14] = 14
        self.cpu.v[15] = 15
        self.cpu.pc = 0xBEEF
        self.cpu.operand = 0xBA
        self.cpu.index = 0xDEAD
        result = str(self.cpu)
        self.assertEqual(
            "PC:0000 OP:00BA V0:00 V1:01 V2:02 V3:03 V4:04 V5:05 V6:06 " +
            "V7:07 V8:08 V9:09 VA:0A VB:0B VC:0C VD:0D VE:0E VF:0F I:DEAD " +
            "DELAY:0 SOUND:0 None", result)

    def test_wait_for_keypress_sets_awaiting_keypress(self):
        self.cpu.operand = 0x0100
        self.cpu.wait_for_keypress()
        self.assertEqual(1, self.cpu.keypress_register)
        self.assertTrue(self.cpu.awaiting_keypress)

    def test_store_subset_regs_one_two(self):
        self.cpu.v[1] = 5
        self.cpu.v[2] = 6
        self.cpu.index = 0x5000
        self.cpu.operand = 0xF122
        self.cpu.store_subset_regs_in_memory()
        self.assertEqual(5, self.cpu.memory[0x5000])
        self.assertEqual(6, self.cpu.memory[0x5001])

    def test_store_subset_regs_one_one(self):
        self.cpu.v[1] = 5
        self.cpu.v[2] = 6
        self.cpu.index = 0x5000
        self.cpu.operand = 0xF112
        self.cpu.store_subset_regs_in_memory()
        self.assertEqual(5, self.cpu.memory[0x5000])
        self.assertEqual(0, self.cpu.memory[0x5001])

    def test_store_subset_regs_three_one(self):
        self.cpu.v[1] = 5
        self.cpu.v[2] = 6
        self.cpu.v[3] = 7
        self.cpu.index = 0x5000
        self.cpu.operand = 0xF312
        self.cpu.store_subset_regs_in_memory()
        self.assertEqual(7, self.cpu.memory[0x5000])
        self.assertEqual(6, self.cpu.memory[0x5001])
        self.assertEqual(5, self.cpu.memory[0x5002])

    def test_store_subset_regs_integration(self):
        self.cpu.v[1] = 5
        self.cpu.v[2] = 6
        self.cpu.v[3] = 7
        self.cpu.index = 0x5000
        self.cpu.memory[0x0200] = 0xF3
        self.cpu.memory[0x0201] = 0x12
        self.cpu.execute_instruction()
        self.assertEqual(7, self.cpu.memory[0x5000])
        self.assertEqual(6, self.cpu.memory[0x5001])
        self.assertEqual(5, self.cpu.memory[0x5002])

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################

"""
Copyright (C) 2012 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A simple Chip 8 emulator - see the README file for more information.
"""
# I M P O R T S ###############################################################

import unittest

from chip8.cpu import Chip8CPU

# C L A S S E S ###############################################################


class TestChip8CPU(unittest.TestCase):
    """
    A test class for the Chip 8 CPU.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.cpu = Chip8CPU(None)

    def test_return_from_subroutine(self):
        """
        00EE - RTS

        Test to make sure that the CPU returns properly from the sepcified
        subroutine. Start at address 0x200 for testing so that we don't run
        into the memory that the stack pointer is going to use.
        """
        for address in range(0x200, 0xFFFF, 0x10):
            self.cpu.memory[self.cpu.registers['sp']] = address & 0x00FF
            self.cpu.memory[self.cpu.registers['sp'] + 1] = \
                (address & 0xFF00) >> 8
            self.cpu.registers['sp'] += 2
            self.cpu.registers['pc'] = 0
            self.cpu.return_from_subroutine()
            self.assertEqual(self.cpu.registers['pc'], address)

    def test_jump_to_address(self):
        """
        1nnn - JUMP nnn

        Test to make sure that the program counter will be set to the correct
        address for any value in the range 0x0FFF during a jump call. Test that
        values above that range will be masked out.
        """
        for address in range(0, 0xFFFF, 0x10):
            self.cpu.operand = address
            self.cpu.registers['pc'] = 0
            self.assertEqual(self.cpu.registers['pc'], 0)
            self.cpu.jump_to_address()
            self.assertEqual(self.cpu.registers['pc'], (address & 0x0FFF))

    def test_jump_to_subroutine(self):
        """
        2nnn - CALL nnn

        Test to make sure that the CPU will call a subroutine properly, and
        save the program counter on the stack.
        """
        for address in range(0x200, 0xFFFF, 0x10):
            self.cpu.operand = address
            self.cpu.registers['sp'] = 0
            self.cpu.registers['pc'] = 0x100
            self.cpu.jump_to_subroutine()
            self.assertEqual(self.cpu.registers['pc'], (address & 0x0FFF))
            self.assertEqual(self.cpu.registers['sp'], 2)
            self.assertEqual(self.cpu.memory[0], 0)
            self.assertEqual(self.cpu.memory[1], 0x1)

    def test_skip_if_reg_equal_value(self):
        """
        3snn - SKE Vs, nn

        Check to make sure that the program counter does not skip the next
        opraion if the register does not equal the value.
        """
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                for reg_value in range(0, 0xFF, 0x10):
                    self.cpu.operand = register << 8
                    self.cpu.operand += value
                    self.cpu.registers['v'][register] = reg_value
                    self.cpu.registers['pc'] = 0
                    self.assertEqual(self.cpu.registers['pc'], 0)
                    self.cpu.skip_if_reg_equal_val()
                    if value == reg_value:
                        self.assertEqual(self.cpu.registers['pc'], 2)
                    else:
                        self.assertEqual(self.cpu.registers['pc'], 0)

    def test_skip_if_reg_not_equal_val(self):
        """
        4snn - SKNE Vs, nn

        Test to make sure that the program counter is incremented only if the
        value in the register is not equal to the value specified.
        """
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                for reg_value in range(0, 0xFF, 0x10):
                    self.cpu.operand = register << 8
                    self.cpu.operand += value
                    self.cpu.registers['v'][register] = reg_value
                    self.cpu.registers['pc'] = 0
                    self.cpu.skip_if_reg_not_equal_val()
                    if value != reg_value:
                        self.assertEqual(self.cpu.registers['pc'], 2)
                    else:
                        self.assertEqual(self.cpu.registers['pc'], 0)

    def test_skip_if_reg_equal_reg(self):
        """
        5st0 - SKE Vs, Vt

        Check to make sure that when all registers are loaded with different
        values, the program counter does not skip.
        """
        for reg_num in range(0x10):
            self.cpu.registers['v'][reg_num] = reg_num

        for reg_1 in range(0x10):
            for reg_2 in range(0x10):
                self.cpu.operand = reg_1
                self.cpu.operand <<= 4
                self.cpu.operand += reg_2
                self.cpu.operand <<= 4

                self.cpu.registers['pc'] = 0
                self.assertEqual(self.cpu.registers['pc'], 0)
                self.cpu.skip_if_reg_equal_reg()

                # If we are testing the same register as the source and the
                # destination, then a skip WILL occur
                if reg_1 == reg_2:
                    self.assertEqual(self.cpu.registers['pc'], 2)
                else:
                    self.assertEqual(self.cpu.registers['pc'], 0)

    def test_move_value_to_reg(self):
        """
        6snn - LOAD Vs, nn

        Loop through registers V0 to VF, and move the value 0x23 into each one
        in turn. Check to make sure that the values of all other registers are
        not modified during the move.
        """
        val = 0x23
        for reg_num in range(0x10):
            self.assertEqual(self.cpu.registers['v'][0x0], 0)

        for reg_num in range(0x10):
            self.cpu.operand = 0x60 + reg_num
            self.cpu.operand <<= 8
            self.cpu.operand += val

            self.cpu.move_value_to_reg()

            for reg_to_check in range(0x10):
                if reg_to_check != reg_num:
                    self.assertEqual(self.cpu.registers['v'][reg_to_check], 0)
                else:
                    self.assertEqual(self.cpu.registers['v'][reg_to_check], val)

            self.cpu.registers['v'][reg_num] = 0

    def test_add_value_to_reg(self):
        """
        7snn - ADD Vs, nn

        Test to make sure the add value to register function works correctly.
        """
        for register in range(0x10):
            for reg_value in range(0, 0xFF, 0x10):
                for value in range(0, 0xFF, 0x10):
                    self.cpu.registers['v'][register] = reg_value
                    self.cpu.operand = register << 8
                    self.cpu.operand += value
                    self.assertEqual(
                        self.cpu.registers['v'][register],
                        reg_value)
                    self.cpu.add_value_to_reg()
                    if value + reg_value < 256:
                        self.assertEqual(
                            self.cpu.registers['v'][register],
                            value + reg_value)
                    else:
                        self.assertEqual(
                            self.cpu.registers['v'][register],
                            (value + reg_value - 256))

    def test_move_reg_into_reg(self):
        """
        8st0 - LOAD Vs, Vt

        Test moving the source register value into the target register.
        """
        for source in range(0x10):
            for target in range(0x10):
                if source != target:
                    self.cpu.registers['v'][target] = 0x32
                    self.cpu.registers['v'][source] = 0
                    self.cpu.operand = source << 8
                    self.cpu.operand += (target << 4)
                    self.cpu.move_reg_into_reg()
                    self.assertEqual(self.cpu.registers['v'][source], 0x32)

    def test_logical_or(self):
        """
        8st1 - OR   Vs, Vt

        Test to make sure that the logical or works correctly.
        """
        for source in range(0x10):
            for target in range(0x10):
                if source != target:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0, 0xFF, 0x10):
                            self.cpu.registers['v'][source] = source_val
                            self.cpu.registers['v'][target] = target_val
                            self.cpu.operand = source << 8
                            self.cpu.operand += (target << 4)
                            self.cpu.logical_or()
                            self.assertEqual(
                                self.cpu.registers['v'][source],
                                source_val | target_val)
                else:
                    for source_val in range(0, 0xFF, 0x10):
                        self.cpu.registers['v'][source] = source_val
                        self.cpu.operand = source << 8
                        self.cpu.operand += (target << 4)
                        self.cpu.logical_or()
                        self.assertEqual(
                            self.cpu.registers['v'][source],
                            source_val)

    def test_logical_and(self):
        """
        8st2 - AND   Vs, Vt

        Test to make sure that the logical and works correctly.
        """
        for source in range(0x10):
            for target in range(0x10):
                if source != target:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0, 0xFF, 0x10):
                            self.cpu.registers['v'][source] = source_val
                            self.cpu.registers['v'][target] = target_val
                            self.cpu.operand = source << 8
                            self.cpu.operand += (target << 4)
                            self.cpu.logical_and()
                            self.assertEqual(
                                self.cpu.registers['v'][source],
                                source_val & target_val)
                else:
                    for source_val in range(256):
                        self.cpu.registers['v'][source] = source_val
                        self.cpu.operand = source << 8
                        self.cpu.operand += (target << 4)
                        self.cpu.logical_and()
                        self.assertEqual(
                            self.cpu.registers['v'][source],
                            source_val)

    def test_exclusive_or(self):
        """
        8st3 - XOR   Vs, Vt

        Test to make sure that the logical xor works correctly.
        """
        for source in range(0x10):
            for target in range(0x10):
                if source != target:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0xF):
                            self.cpu.registers['v'][source] = source_val
                            self.cpu.registers['v'][target] = target_val
                            self.cpu.operand = source << 8
                            self.cpu.operand += (target << 4)
                            self.cpu.exclusive_or()
                            self.assertEqual(
                                self.cpu.registers['v'][source],
                                source_val ^ target_val)

    def test_add_to_reg(self):
        """
        8st4 - ADD  Vs, Vt

        Test to make sure that the add function properly adds two numbers
        together, setting the overflow bit when necessary.
        """
        for source in range(0xF):
            for target in range(0xF):
                if source != target:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0, 0xFF, 0x10):
                            self.cpu.registers['v'][source] = source_val
                            self.cpu.registers['v'][target] = target_val
                            self.cpu.operand = source << 8
                            self.cpu.operand += (target << 4)
                            self.cpu.add_reg_to_reg()
                            if source_val + target_val > 255:
                                self.assertEqual(
                                    self.cpu.registers['v'][source],
                                    source_val + target_val - 256)
                                self.assertEqual(
                                    self.cpu.registers['v'][0xF], 1)
                            else:
                                self.assertEqual(
                                    self.cpu.registers['v'][source],
                                    source_val + target_val)
                                self.assertEqual(
                                    self.cpu.registers['v'][0xF], 0)

    def test_subtract_reg_from_reg(self):
        """
        8st5 - SUB  Vs, Vt

        Test to make sure that the subtract function properly subs two numbers
        correctly, setting the overflow bit when necessary.
        """
        for source in range(0xF):
            for target in range(0xF):
                if source != target:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0xF):
                            self.cpu.registers['v'][source] = source_val
                            self.cpu.registers['v'][target] = target_val
                            self.cpu.operand = source << 8
                            self.cpu.operand += (target << 4)
                            self.cpu.subtract_reg_from_reg()
                            if source_val > target_val:
                                self.assertEqual(
                                    self.cpu.registers['v'][source],
                                    source_val - target_val)
                                self.assertEqual(
                                    self.cpu.registers['v'][0xF], 1)
                            else:
                                self.assertEqual(
                                    self.cpu.registers['v'][source],
                                    256 + source_val - target_val)
                                self.assertEqual(
                                    self.cpu.registers['v'][0xF], 0)

    def test_right_shift_reg(self):
        """
        8s06 - SHR  Vs

        Test to make sure that bit shifting properly shifts values to the
        right.
        """
        for register in range(0xF):
            for value in range(0, 0xFF, 0x10):
                self.cpu.registers['v'][register] = value
                self.cpu.operand = register << 8
                for index in range(1, 8):
                    shifted_val = value >> index
                    self.cpu.registers['v'][0xF] = 0
                    bit_zero = self.cpu.registers['v'][register] & 0x1
                    self.cpu.right_shift_reg()
                    self.assertEqual(
                        self.cpu.registers['v'][register], shifted_val)
                    self.assertEqual(self.cpu.registers['v'][0xF], bit_zero)

    def test_subtract_reg_from_reg1(self):
        """
        8st7 - SUBN Vs, Vt

        Test to make sure that the subtract function properly subs two numbers
        correctly, setting the overflow bit when necessary.
        """
        for source in range(0xF):
            for target in range(0xF):
                if source != target:
                    for source_val in range(0, 0xFF, 0x10):
                        for target_val in range(0xF):
                            self.cpu.registers['v'][source] = source_val
                            self.cpu.registers['v'][target] = target_val
                            self.cpu.operand = source << 8
                            self.cpu.operand += (target << 4)
                            self.cpu.subtract_reg_from_reg1()
                            if target_val > source_val:
                                self.assertEqual(
                                    self.cpu.registers['v'][source],
                                    target_val - source_val)
                                self.assertEqual(
                                    self.cpu.registers['v'][0xF], 1)
                            else:
                                self.assertEqual(
                                    self.cpu.registers['v'][source],
                                    256 + target_val - source_val)
                                self.assertEqual(
                                    self.cpu.registers['v'][0xF], 0)

    def test_left_shift_reg(self):
        """
        8s0E - SHR  Vs

        Test to make sure that bit shifting properly shifts values to the
        left.
        """
        for register in range(0xF):
            for value in range(256):
                self.cpu.registers['v'][register] = value
                self.cpu.operand = register << 8
                for index in range(1, 8):
                    shifted_val = value << index
                    bit_seven = (shifted_val & 0x100) >> 9
                    shifted_val = shifted_val & 0xFFFF
                    self.cpu.registers['v'][0xF] = 0
                    self.cpu.left_shift_reg()
                    self.assertEqual(
                        self.cpu.registers['v'][register],
                        shifted_val)
                    self.assertEqual(self.cpu.registers['v'][0xF], bit_seven)

    def test_skip_if_reg_not_equal_reg(self):
        """
        9st0 - SKNE Vs, Vt

        Test to make sure skip if source not equal target register works.
        """
        for register in range(0x10):
            self.cpu.registers['v'][register] = register

        for source in range(0x10):
            for target in range(0x10):
                self.cpu.operand = source << 8
                self.cpu.operand += (target << 4)
                self.cpu.registers['pc'] = 0
                self.cpu.skip_if_reg_not_equal_reg()
                if source != target:
                    self.assertEqual(self.cpu.registers['pc'], 2)
                else:
                    self.assertEqual(self.cpu.registers['pc'], 0)

    def test_load_index_reg_with_value(self):
        """
        Annn - LOAD I, nnn

        Test loading values into the index register.
        """
        for value in range(0x10000):
            self.cpu.operand = value
            self.cpu.load_index_reg_with_value()
            self.assertEqual(self.cpu.registers['index'], value & 0x0FFF)

    def test_jump_to_index_plus_value(self):
        """
        Bnnn - JUMP [I] + nnn

        Test jump to index plus value.
        """
        for index in range(0, 0xFFF, 0x10):
            for value in range(0, 0xFFF, 0x10):
                self.cpu.registers['index'] = index
                self.cpu.registers['pc'] = 0
                self.cpu.operand = value
                self.cpu.jump_to_index_plus_value()
                self.assertEqual(index + value, self.cpu.registers['pc'])

    def test_generate_random_number(self):
        """
        Csnn - RAND Vs, nn

        Test generating random numbers. Since we can't control the random
        number generated (well, we can by setting a seed and enumerating
        the numbers), generate random numbers for each register, and
        ensure that they are between 0 and 255.
        """
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                self.cpu.registers['v'][register] = -1
                self.cpu.operand = register << 8
                self.cpu.operand += value
                self.cpu.generate_random_number()
                self.assertTrue(self.cpu.registers['v'][register] >= 0)
                self.assertTrue(self.cpu.registers['v'][register] <= 255)

    def test_move_delay_timer_into_reg(self):
        """
        Fn07 - LOAD Vs, DELAY

        Test to make sure the delay values are moved correctly into the
        specified registers.
        """
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                self.cpu.timers['delay'] = value
                self.cpu.operand = register << 8
                self.cpu.registers['v'][register] = 0
                self.cpu.move_delay_timer_into_reg()
                self.assertEqual(self.cpu.registers['v'][register], value)

    def test_move_reg_into_delay_timer(self):
        """
        Fn15 - LOAD DELAY, Vs

        Test to make sure the register values are moved correctly into the
        delay timer register.
        """
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                self.cpu.registers['v'][register] = value
                self.cpu.operand = register << 8
                self.cpu.timers['delay'] = 0
                self.cpu.move_reg_into_delay_timer()
                self.assertEqual(self.cpu.timers['delay'], value)

    def test_move_reg_into_sound_timer(self):
        """
        Fn18 - LOAD SOUND, Vs

        Test to make sure the register values are moved correctly into the
        sound timer register.
        """
        for register in range(0x10):
            for value in range(0, 0xFF, 0x10):
                self.cpu.registers['v'][register] = value
                self.cpu.operand = register << 8
                self.cpu.timers['sound'] = 0
                self.cpu.move_reg_into_sound_timer()
                self.assertEqual(self.cpu.timers['sound'], value)

    def test_add_reg_into_index(self):
        """
        Fs1E - ADD I, Vs

        Test to make sure adding register into index works correctly.
        """
        for register in range(0x10):
            for index in range(0, 0xFFF, 0x10):
                self.cpu.registers['index'] = index
                self.cpu.registers['v'][register] = 0x89
                self.cpu.operand = (register << 8)
                self.cpu.add_reg_into_index()
                self.assertEqual(index + 0x89, self.cpu.registers['index'])

    def test_load_index_with_reg_sprite(self):
        """
        Fn29 - LOAD I, Vn

        Test to make sure that the correct index value for each of the
        characters is loaded into the index register. All character sprites
        are 5 bytes long, and begin at 0x0000, thus the index register
        should be loaded with the number to display x 5.
        """
        for number in range(0x10):
            self.cpu.registers['index'] = 0xFFF
            self.cpu.registers['v'][0] = number
            self.cpu.operand = 0xF029
            self.cpu.load_index_with_reg_sprite()
            self.assertEqual(number * 5, self.cpu.registers['index'])

    def test_store_bcd_in_memory(self):
        """
        Fn33 - BCD

        Test to make sure that a binary coded decimal is being stored in
        memory correctly.
        """
        for number in range(0x100):
            number_as_string = '{:03d}'.format(number)
            self.cpu.registers['index'] = 0
            self.cpu.registers['v'][0] = number
            self.cpu.operand = 0xF033
            self.cpu.store_bcd_in_memory()
            self.assertEqual(int(number_as_string[0]), self.cpu.memory[0])
            self.assertEqual(int(number_as_string[1]), self.cpu.memory[1])
            self.assertEqual(int(number_as_string[2]), self.cpu.memory[2])

    def test_store_regs_in_memory(self):
        """
        Fs55 - STOR [I], Vs

        Test to make sure storing registers in memory works.
        """
        for register in range(0x10):
            self.cpu.registers['v'][register] = register
            self.cpu.operand = (register << 8)
            self.cpu.store_regs_in_memory()
            self.cpu.registers['index'] = 0
            for counter in range(register):
                self.assertEqual(counter, self.cpu.memory[counter])

    def test_read_regs_from_memory(self):
        """
        Fn65 - LOAD Vn, [I]

        Test that loading register values from memory loads the correct values
        into the correct registers.
        """
        index = 0x500
        self.cpu.registers['index'] = index

        for register in range(0xF):
            self.cpu.memory[index + register] = register + 0x89

        for register in range(0xF):
            for reg_to_set in range(0xF):
                self.cpu.registers['v'][reg_to_set] = 0

            self.cpu.operand = 0xF000
            self.cpu.operand += (register << 8)
            self.cpu.operand += 0x65
            self.cpu.read_regs_from_memory()
            for reg_to_check in range(0xF):
                if reg_to_check > register:
                    self.assertEqual(self.cpu.registers['v'][reg_to_check], 0)
                else:
                    self.assertEqual(
                        self.cpu.registers['v'][reg_to_check],
                        reg_to_check + 0x89)

    def test_load_rom(self):
        """
        Test to make sure we can read a ROM file into specified memory
        location.
        """
        self.cpu.load_rom('test/romfile', 0)
        self.assertEqual(ord('a'), self.cpu.memory[0])
        self.assertEqual(ord('b'), self.cpu.memory[1])
        self.assertEqual(ord('c'), self.cpu.memory[2])
        self.assertEqual(ord('d'), self.cpu.memory[3])
        self.assertEqual(ord('e'), self.cpu.memory[4])
        self.assertEqual(ord('f'), self.cpu.memory[5])
        self.assertEqual(ord('g'), self.cpu.memory[6])

    def test_decrement_timers_decrements_by_one(self):
        """
        Test to make sure both sound and delay timers will decrement when
        called.
        """
        self.cpu.timers['delay'] = 2
        self.cpu.timers['sound'] = 2
        self.cpu.decrement_timers()
        self.assertEqual(1, self.cpu.timers['delay'])
        self.assertEqual(1, self.cpu.timers['sound'])

    def test_decrement_timers_does_not_go_negative(self):
        """
        Test to make sure that the timers will not go below 0.
        """
        self.cpu.timers['delay'] = 0
        self.cpu.timers['sound'] = 0
        self.cpu.decrement_timers()
        self.assertEqual(0, self.cpu.timers['delay'])
        self.assertEqual(0, self.cpu.timers['sound'])

# M A I N #####################################################################

if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################

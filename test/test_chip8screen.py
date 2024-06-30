"""
Copyright (C) 2024 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A simple Chip 8 emulator - see the README file for more information.
"""
# I M P O R T S ###############################################################

import unittest

from chip8.screen import Chip8Screen

# C L A S S E S ###############################################################


class TestChip8Screen(unittest.TestCase):
    """
    A test class for the Chip 8 Screen.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.screen = Chip8Screen(2)

    def test_get_width_normal(self):
        self.assertEqual(64, self.screen.get_width())

    def test_get_width_extended(self):
        self.screen.set_extended()
        self.assertEqual(128, self.screen.get_width())

    def test_get_height_normal(self):
        self.assertEqual(32, self.screen.get_height())

    def test_get_height_extended(self):
        self.screen.set_extended()
        self.assertEqual(64, self.screen.get_height())

    def test_all_pixels_off_on_screen_init(self):
        self.screen.init_display()
        for x_pos in range(64):
            for y_pos in range(32):
                self.assertEqual(0, self.screen.get_pixel(x_pos, y_pos, 1))
                self.assertEqual(0, self.screen.get_pixel(x_pos, y_pos, 2))

    def test_get_pixel_on_bitplane_0_returns_false(self):
        self.screen.init_display()
        for xpos in range(64):
            for ypos in range(32):
                self.screen.draw_pixel(xpos, ypos, 1, 1)
                self.screen.draw_pixel(xpos, ypos, 1, 2)
                self.assertFalse(self.screen.get_pixel(xpos, ypos, 0))

    def test_write_pixel_turns_on_pixel_on_bitplane(self):
        self.screen.init_display()
        for xpos in range(64):
            for ypos in range(32):
                self.screen.draw_pixel(xpos, ypos, 1, 1)
                self.assertTrue(self.screen.get_pixel(xpos, ypos, 1))
                self.assertFalse(self.screen.get_pixel(xpos, ypos, 2))

    def test_write_pixel_turns_on_pixel_on_both_bitplanes(self):
        self.screen.init_display()
        for xpos in range(64):
            for ypos in range(32):
                self.screen.draw_pixel(xpos, ypos, 1, 3)
                self.assertTrue(self.screen.get_pixel(xpos, ypos, 1))
                self.assertTrue(self.screen.get_pixel(xpos, ypos, 2))

    def test_write_pixel_does_nothing_on_bitplane_0(self):
        self.screen.init_display()
        for xpos in range(64):
            for ypos in range(32):
                self.screen.draw_pixel(xpos, ypos, 1, 0)
                self.assertFalse(self.screen.get_pixel(xpos, ypos, 1))
                self.assertFalse(self.screen.get_pixel(xpos, ypos, 2))

    def test_clear_screen_clears_pixels_on_bitplane_1(self):
        self.screen.init_display()
        for x_pos in range(64):
            for y_pos in range(32):
                self.screen.draw_pixel(x_pos, y_pos, 1, 1)
        self.screen.clear_screen(1)
        for x_pos in range(64):
            for y_pos in range(32):
                self.assertFalse(self.screen.get_pixel(x_pos, y_pos, 1))
                self.assertFalse(self.screen.get_pixel(x_pos, y_pos, 2))

    def test_clear_screen_clears_pixels_on_bitplane_1_only_when_both_set(self):
        self.screen.init_display()
        for x_pos in range(64):
            for y_pos in range(32):
                self.screen.draw_pixel(x_pos, y_pos, 1, 1)
                self.screen.draw_pixel(x_pos, y_pos, 1, 2)
        self.screen.clear_screen(1)
        for x_pos in range(64):
            for y_pos in range(32):
                self.assertFalse(self.screen.get_pixel(x_pos, y_pos, 1))
                self.assertTrue(self.screen.get_pixel(x_pos, y_pos, 2))

    def test_clear_screen_on_bitplane_0_does_nothing(self):
        self.screen.init_display()
        for xpos in range(64):
            for ypos in range(32):
                self.screen.draw_pixel(xpos, ypos, 1, 1)
                self.screen.draw_pixel(xpos, ypos, 1, 2)
        self.screen.clear_screen(0)
        for xpos in range(64):
            for ypos in range(32):
                self.assertTrue(self.screen.get_pixel(xpos, ypos, 1))
                self.assertTrue(self.screen.get_pixel(xpos, ypos, 2))

    def test_scroll_down_bitplane_0_does_nothing(self):
        self.screen.init_display()
        self.screen.draw_pixel(0, 0, 1, 1)
        self.screen.draw_pixel(0, 0, 1, 2)
        self.assertTrue(self.screen.get_pixel(0, 0, 1))
        self.assertTrue(self.screen.get_pixel(0, 0, 2))
        self.screen.scroll_down(1, 0)
        self.assertTrue(self.screen.get_pixel(0, 0, 1))
        self.assertTrue(self.screen.get_pixel(0, 0, 2))
        self.assertFalse(self.screen.get_pixel(0, 1, 1))
        self.assertFalse(self.screen.get_pixel(0, 1, 2))

    def test_scroll_down_bitplane_1(self):
        self.screen.init_display()
        self.screen.draw_pixel(0, 0, 1, 1)
        self.assertTrue(self.screen.get_pixel(0, 0, 1))
        self.assertFalse(self.screen.get_pixel(0, 0, 2))
        self.screen.scroll_down(1, 1)
        self.assertFalse(self.screen.get_pixel(0, 0, 1))
        self.assertFalse(self.screen.get_pixel(0, 0, 2))
        self.assertTrue(self.screen.get_pixel(0, 1, 1))
        self.assertFalse(self.screen.get_pixel(0, 1, 2))

    def test_scroll_down_bitplane_1_both_pixels_active(self):
        self.screen.init_display()
        self.screen.draw_pixel(0, 0, 1, 1)
        self.screen.draw_pixel(0, 0, 1, 2)
        self.assertTrue(self.screen.get_pixel(0, 0, 1))
        self.assertTrue(self.screen.get_pixel(0, 0, 2))
        self.screen.scroll_down(1, 1)
        self.assertFalse(self.screen.get_pixel(0, 0, 1))
        self.assertTrue(self.screen.get_pixel(0, 0, 2))
        self.assertTrue(self.screen.get_pixel(0, 1, 1))
        self.assertFalse(self.screen.get_pixel(0, 1, 2))

    def test_scroll_down_bitplane_3_both_pixels_active(self):
        self.screen.init_display()
        self.screen.draw_pixel(0, 0, 1, 1)
        self.screen.draw_pixel(0, 0, 1, 2)
        self.assertTrue(self.screen.get_pixel(0, 0, 1))
        self.assertTrue(self.screen.get_pixel(0, 0, 2))
        self.screen.scroll_down(1, 3)
        self.assertFalse(self.screen.get_pixel(0, 0, 1))
        self.assertFalse(self.screen.get_pixel(0, 0, 2))
        self.assertTrue(self.screen.get_pixel(0, 1, 1))
        self.assertTrue(self.screen.get_pixel(0, 1, 2))

    def test_scroll_right_bitplane_0_does_nothing(self):
        self.screen.init_display()
        self.screen.draw_pixel(0, 0, 1, 1)
        self.screen.draw_pixel(0, 0, 1, 2)
        self.assertTrue(self.screen.get_pixel(0, 0, 1))
        self.assertTrue(self.screen.get_pixel(0, 0, 2))
        self.screen.scroll_right(0)
        self.assertTrue(self.screen.get_pixel(0, 0, 1))
        self.assertFalse(self.screen.get_pixel(1, 0, 1))
        self.assertFalse(self.screen.get_pixel(2, 0, 1))
        self.assertFalse(self.screen.get_pixel(3, 0, 1))
        self.assertFalse(self.screen.get_pixel(4, 0, 1))
        self.assertTrue(self.screen.get_pixel(0, 0, 2))
        self.assertFalse(self.screen.get_pixel(1, 0, 2))
        self.assertFalse(self.screen.get_pixel(2, 0, 2))
        self.assertFalse(self.screen.get_pixel(3, 0, 2))
        self.assertFalse(self.screen.get_pixel(4, 0, 2))

    def test_scroll_right_bitplane_1(self):
        self.screen.init_display()
        self.screen.draw_pixel(0, 0, 1, 1)
        self.assertTrue(self.screen.get_pixel(0, 0, 1))
        self.assertFalse(self.screen.get_pixel(0, 0, 2))
        self.screen.scroll_right(1)
        self.assertFalse(self.screen.get_pixel(0, 0, 1))
        self.assertFalse(self.screen.get_pixel(1, 0, 1))
        self.assertFalse(self.screen.get_pixel(2, 0, 1))
        self.assertFalse(self.screen.get_pixel(3, 0, 1))
        self.assertTrue(self.screen.get_pixel(4, 0, 1))
        self.assertFalse(self.screen.get_pixel(0, 0, 2))
        self.assertFalse(self.screen.get_pixel(1, 0, 2))
        self.assertFalse(self.screen.get_pixel(2, 0, 2))
        self.assertFalse(self.screen.get_pixel(3, 0, 2))
        self.assertFalse(self.screen.get_pixel(4, 0, 2))

    def test_scroll_right_bitplane_1_both_pixels_active(self):
        self.screen.init_display()
        self.screen.draw_pixel(0, 0, 1, 1)
        self.screen.draw_pixel(0, 0, 1, 2)
        self.assertTrue(self.screen.get_pixel(0, 0, 1))
        self.assertTrue(self.screen.get_pixel(0, 0, 2))
        self.screen.scroll_right(1)
        self.assertFalse(self.screen.get_pixel(0, 0, 1))
        self.assertFalse(self.screen.get_pixel(1, 0, 1))
        self.assertFalse(self.screen.get_pixel(2, 0, 1))
        self.assertFalse(self.screen.get_pixel(3, 0, 1))
        self.assertTrue(self.screen.get_pixel(4, 0, 1))
        self.assertTrue(self.screen.get_pixel(0, 0, 2))
        self.assertFalse(self.screen.get_pixel(1, 0, 2))
        self.assertFalse(self.screen.get_pixel(2, 0, 2))
        self.assertFalse(self.screen.get_pixel(3, 0, 2))
        self.assertFalse(self.screen.get_pixel(4, 0, 2))

    def test_scroll_right_bitplane_3_both_pixels_active(self):
        self.screen.init_display()
        self.screen.draw_pixel(0, 0, 1, 1)
        self.screen.draw_pixel(0, 0, 1, 2)
        self.assertTrue(self.screen.get_pixel(0, 0, 1))
        self.assertTrue(self.screen.get_pixel(0, 0, 2))
        self.screen.scroll_right(3)
        self.assertFalse(self.screen.get_pixel(0, 0, 1))
        self.assertFalse(self.screen.get_pixel(1, 0, 1))
        self.assertFalse(self.screen.get_pixel(2, 0, 1))
        self.assertFalse(self.screen.get_pixel(3, 0, 1))
        self.assertTrue(self.screen.get_pixel(4, 0, 1))
        self.assertFalse(self.screen.get_pixel(0, 0, 2))
        self.assertFalse(self.screen.get_pixel(1, 0, 2))
        self.assertFalse(self.screen.get_pixel(2, 0, 2))
        self.assertFalse(self.screen.get_pixel(3, 0, 2))
        self.assertTrue(self.screen.get_pixel(4, 0, 2))

    def test_scroll_left_bitplane_0_does_nothing(self):
        self.screen.init_display()
        self.screen.draw_pixel(63, 0, 1, 1)
        self.screen.draw_pixel(63, 0, 1, 2)
        self.assertTrue(self.screen.get_pixel(63, 0, 1))
        self.assertTrue(self.screen.get_pixel(63, 0, 2))
        self.screen.scroll_left(0)
        self.assertTrue(self.screen.get_pixel(63, 0, 1))
        self.assertFalse(self.screen.get_pixel(62, 0, 1))
        self.assertFalse(self.screen.get_pixel(61, 0, 1))
        self.assertFalse(self.screen.get_pixel(60, 0, 1))
        self.assertFalse(self.screen.get_pixel(59, 0, 1))
        self.assertTrue(self.screen.get_pixel(63, 0, 2))
        self.assertFalse(self.screen.get_pixel(62, 0, 2))
        self.assertFalse(self.screen.get_pixel(61, 0, 2))
        self.assertFalse(self.screen.get_pixel(60, 0, 2))
        self.assertFalse(self.screen.get_pixel(59, 0, 2))

    def test_scroll_left_bitplane_1(self):
        self.screen.init_display()
        self.screen.draw_pixel(63, 0, 1, 1)
        self.assertTrue(self.screen.get_pixel(63, 0, 1))
        self.assertFalse(self.screen.get_pixel(63, 0, 2))
        self.screen.scroll_left(1)
        self.assertFalse(self.screen.get_pixel(63, 0, 1))
        self.assertFalse(self.screen.get_pixel(62, 0, 1))
        self.assertFalse(self.screen.get_pixel(61, 0, 1))
        self.assertFalse(self.screen.get_pixel(60, 0, 1))
        self.assertTrue(self.screen.get_pixel(59, 0, 1))
        self.assertFalse(self.screen.get_pixel(63, 0, 2))
        self.assertFalse(self.screen.get_pixel(62, 0, 2))
        self.assertFalse(self.screen.get_pixel(61, 0, 2))
        self.assertFalse(self.screen.get_pixel(60, 0, 2))
        self.assertFalse(self.screen.get_pixel(59, 0, 2))

    def test_scroll_left_bitplane_1_both_pixels_active(self):
        self.screen.init_display()
        self.screen.draw_pixel(63, 0, 1, 1)
        self.screen.draw_pixel(63, 0, 1, 2)
        self.assertTrue(self.screen.get_pixel(63, 0, 1))
        self.assertTrue(self.screen.get_pixel(63, 0, 2))
        self.screen.scroll_left(1)
        self.assertFalse(self.screen.get_pixel(63, 0, 1))
        self.assertFalse(self.screen.get_pixel(62, 0, 1))
        self.assertFalse(self.screen.get_pixel(61, 0, 1))
        self.assertFalse(self.screen.get_pixel(60, 0, 1))
        self.assertTrue(self.screen.get_pixel(59, 0, 1))
        self.assertTrue(self.screen.get_pixel(63, 0, 2))
        self.assertFalse(self.screen.get_pixel(62, 0, 2))
        self.assertFalse(self.screen.get_pixel(61, 0, 2))
        self.assertFalse(self.screen.get_pixel(60, 0, 2))
        self.assertFalse(self.screen.get_pixel(59, 0, 2))

    def test_scroll_left_bitplane_3_both_pixels_active(self):
        self.screen.init_display()
        self.screen.draw_pixel(63, 0, 1, 1)
        self.screen.draw_pixel(63, 0, 1, 2)
        self.assertTrue(self.screen.get_pixel(63, 0, 1))
        self.assertTrue(self.screen.get_pixel(63, 0, 2))
        self.screen.scroll_left(3)
        self.assertFalse(self.screen.get_pixel(63, 0, 1))
        self.assertFalse(self.screen.get_pixel(62, 0, 1))
        self.assertFalse(self.screen.get_pixel(61, 0, 1))
        self.assertFalse(self.screen.get_pixel(60, 0, 1))
        self.assertTrue(self.screen.get_pixel(59, 0, 1))
        self.assertFalse(self.screen.get_pixel(63, 0, 2))
        self.assertFalse(self.screen.get_pixel(62, 0, 2))
        self.assertFalse(self.screen.get_pixel(61, 0, 2))
        self.assertFalse(self.screen.get_pixel(60, 0, 2))
        self.assertTrue(self.screen.get_pixel(59, 0, 2))

    def test_set_normal(self):
        self.screen.init_display()
        self.screen.set_extended()
        self.screen.set_normal()
        self.assertEqual(64, self.screen.get_width())
        self.assertEqual(32, self.screen.get_height())


# M A I N #####################################################################

if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################

"""
Copyright (C) 2012 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A simple Chip 8 emulator - see the README file for more information.
"""
# I M P O R T S ###############################################################

import unittest

from chip8.screen import (
    Chip8Screen, SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_MODE_NORMAL
)

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

    def test_get_width(self):
        self.assertEqual(SCREEN_WIDTH[SCREEN_MODE_NORMAL], self.screen.get_width())

    def test_get_height(self):
        self.assertEqual(SCREEN_HEIGHT[SCREEN_MODE_NORMAL], self.screen.get_height())

    def test_all_pixels_off_on_screen_init(self):
        self.screen.init_display()
        for x_pos in range(SCREEN_WIDTH[SCREEN_MODE_NORMAL]):
            for y_pos in range(SCREEN_HEIGHT[SCREEN_MODE_NORMAL]):
                self.assertEqual(0, self.screen.get_pixel(x_pos, y_pos))

    def test_write_pixel_turns_on_pixel(self):
        self.screen.init_display()
        for xpos in range(SCREEN_WIDTH[SCREEN_MODE_NORMAL]):
            for ypos in range(SCREEN_HEIGHT[SCREEN_MODE_NORMAL]):
                self.screen.draw_pixel(xpos, ypos, 1)
                self.assertEqual(1, self.screen.get_pixel(xpos, ypos))

    def test_clear_screen_clears_pixels(self):
        self.screen.init_display()
        for x_pos in range(SCREEN_WIDTH[SCREEN_MODE_NORMAL]):
            for y_pos in range(SCREEN_HEIGHT[SCREEN_MODE_NORMAL]):
                self.screen.draw_pixel(x_pos, y_pos, 1)
        self.screen.clear_screen()
        for x_pos in range(SCREEN_WIDTH[SCREEN_MODE_NORMAL]):
            for y_pos in range(SCREEN_HEIGHT[SCREEN_MODE_NORMAL]):
                self.assertEqual(0, self.screen.get_pixel(x_pos, y_pos))

    def test_scroll_down(self):
        self.screen.init_display()
        self.screen.draw_pixel(0, 0, 1)
        self.screen.scroll_down(1)
        self.assertEqual(0, self.screen.get_pixel(0, 0))
        self.assertEqual(1, self.screen.get_pixel(0, 1))

    def test_scroll_right(self):
        self.screen.init_display()
        self.screen.draw_pixel(0, 0, 1)
        self.screen.scroll_right()
        self.assertEqual(0, self.screen.get_pixel(0, 0))
        self.assertEqual(0, self.screen.get_pixel(1, 0))
        self.assertEqual(0, self.screen.get_pixel(2, 0))
        self.assertEqual(0, self.screen.get_pixel(3, 0))
        self.assertEqual(1, self.screen.get_pixel(4, 0))

    def test_scroll_left(self):
        self.screen.init_display()
        self.screen.draw_pixel(63, 0, 1)
        self.screen.scroll_left()
        self.assertEqual(0, self.screen.get_pixel(63, 0))
        self.assertEqual(0, self.screen.get_pixel(62, 0))
        self.assertEqual(0, self.screen.get_pixel(61, 0))
        self.assertEqual(0, self.screen.get_pixel(60, 0))
        self.assertEqual(1, self.screen.get_pixel(59, 0))

    def test_set_extended(self):
        self.screen.init_display()
        self.screen.set_extended()
        self.assertEqual(128, self.screen.width)
        self.assertEqual(64, self.screen.height)

    def test_set_normal(self):
        self.screen.init_display()
        self.screen.set_extended()
        self.screen.set_normal()
        self.assertEqual(64, self.screen.width)
        self.assertEqual(32, self.screen.height)


# M A I N #####################################################################

if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################

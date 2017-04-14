"""
Copyright (C) 2012 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A simple Chip 8 emulator - see the README file for more information.
"""
# I M P O R T S ###############################################################

import unittest

from chip8.screen import Chip8Screen, SCREEN_WIDTH, SCREEN_HEIGHT

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
        """
        Ensure that the screen width is set correctly.
        """
        self.assertEqual(SCREEN_WIDTH, self.screen.get_width())

    def test_get_height(self):
        """
        Ensure that the screen height is set correctly.
        """
        self.assertEqual(SCREEN_HEIGHT, self.screen.get_height())

    def test_all_pixels_off_on_screen_init(self):
        """
        Ensure that the screen starts up blank.
        """
        self.screen.init_display()
        for x_pos in range(SCREEN_WIDTH):
            for y_pos in range(SCREEN_HEIGHT):
                self.assertEqual(0, self.screen.get_pixel(x_pos, y_pos))

    def test_write_pixel_turns_on_pixel(self):
        """
        Ensure that the screen pixels can be written.
        """
        self.screen.init_display()
        for xpos in range(SCREEN_WIDTH):
            for ypos in range(SCREEN_HEIGHT):
                self.screen.draw_pixel(xpos, ypos, 1)
                self.assertEqual(1, self.screen.get_pixel(xpos, ypos))

    def test_clear_screen_clears_pixels(self):
        """
        Ensure that all pixels are off after clearing the screen.
        """
        self.screen.init_display()
        for x_pos in range(SCREEN_WIDTH):
            for y_pos in range(SCREEN_HEIGHT):
                self.screen.draw_pixel(x_pos, y_pos, 1)
        self.screen.clear_screen()
        for x_pos in range(SCREEN_WIDTH):
            for y_pos in range(SCREEN_HEIGHT):
                self.assertEqual(0, self.screen.get_pixel(x_pos, y_pos))


# M A I N #####################################################################

if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################

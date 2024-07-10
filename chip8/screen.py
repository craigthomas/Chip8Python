"""
Copyright (C) 2012 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A Chip 8 Screen - see the README file for more information.
"""
# I M P O R T S ###############################################################

from pygame import display, HWSURFACE, DOUBLEBUF, Color, draw

# C O N S T A N T S ###########################################################

# Various screen modes
SCREEN_MODE_NORMAL = 0
SCREEN_MODE_EXTENDED = 1

# The depth of the screen is the number of bits used to represent the color
# of a pixel.
SCREEN_DEPTH = 8

# C L A S S E S ###############################################################


class Chip8Screen:
    """
    A class to emulate a Chip 8 Screen. The original Chip 8 screen was 64 x 32
    with 2 colors. In this emulator, this translates to color 0 (off) and color
    1 (on).
    """
    def __init__(
            self,
            scale_factor,
            color_0="000000",
            color_1="ff33cc",
            color_2="33ccff",
            color_3="FFFFFF"
    ):
        """
        Initializes the main screen. The scale factor is used to modify
        the size of the main screen, since the original resolution of the
        Chip 8 was 64 x 32, which is quite small.

        :param scale_factor: the scaling factor to apply to the screen
        """
        self.height = 64
        self.width = 128
        self.scale_factor = scale_factor
        self.surface = None
        self.mode = SCREEN_MODE_NORMAL
        self.pixel_colors = {
            0: Color(f"#{color_0}"),
            1: Color(f"#{color_1}"),
            2: Color(f"#{color_2}"),
            3: Color(f"#{color_3}"),
        }

    def init_display(self):
        """
        Attempts to initialize a screen with the specified height and width.
        The screen will by default be of depth SCREEN_DEPTH, and will be
        double-buffered in hardware (if possible).
        """
        display.init()
        self.surface = display.set_mode(
            ((self.width * self.scale_factor),
             (self.height * self.scale_factor)),
            HWSURFACE | DOUBLEBUF,
            SCREEN_DEPTH)
        display.set_caption('CHIP8 Emulator')
        self.clear_screen(3)
        self.update()

    def draw_pixel(self, x_pos, y_pos, turn_on, bitplane):
        """
        Turn a pixel on or off at the specified location on the screen. Note
        that the pixel will not automatically be drawn on the screen, you
        must call the update() function to flip the drawing buffer to the
        display. The coordinate system starts with (0, 0) being in the top
        left of the screen.

        :param x_pos: the x coordinate to place the pixel
        :param y_pos: the y coordinate to place the pixel
        :param turn_on: whether to turn the pixel on or off
        :param bitplane: the bitplane where the pixel is located
        """
        if bitplane == 0:
            return

        other_bitplane = 2 if bitplane == 1 else 1
        other_pixel_on = self.get_pixel(x_pos, y_pos, other_bitplane)

        mode_scale = 1 if self.mode == SCREEN_MODE_EXTENDED else 2
        x_base = (x_pos * mode_scale) * self.scale_factor
        y_base = (y_pos * mode_scale) * self.scale_factor

        if turn_on and other_pixel_on:
            pixel_color = 3
        elif turn_on and not other_pixel_on:
            pixel_color = bitplane
        elif not turn_on and other_pixel_on:
            pixel_color = other_bitplane
        else:
            pixel_color = 0

        draw.rect(self.surface,
                  self.pixel_colors[pixel_color],
                  (x_base, y_base, mode_scale * self.scale_factor, mode_scale * self.scale_factor))

    def get_pixel(self, x_pos, y_pos, bitplane):
        """
        Returns whether the pixel is on (1) or off (0) at the specified
        location for the specified bitplane.

        :param x_pos: the x coordinate to check
        :param y_pos: the y coordinate to check
        :param bitplane: the bitplane where the pixel is located
        :return: True if the pixel is currently turned on, False otherwise
        """
        if bitplane == 0:
            return False

        mode_scale = 1 if self.mode == SCREEN_MODE_EXTENDED else 2
        x_scale = (x_pos * mode_scale) * self.scale_factor
        y_scale = (y_pos * mode_scale) * self.scale_factor
        pixel_color = self.surface.get_at((x_scale, y_scale))
        return pixel_color == self.pixel_colors[bitplane] or pixel_color == self.pixel_colors[3]

    def get_width(self):
        """
        Returns the width of the screen in pixels.

        :return: the width of the screen
        """
        return 128 if self.mode == SCREEN_MODE_EXTENDED else 64

    def get_height(self):
        """
        Returns the height of the screen in pixels.

        :return: the height of the screen
        """
        return 64 if self.mode == SCREEN_MODE_EXTENDED else 32

    def clear_screen(self, bitplane):
        """
        Turns off all the pixels on the specified bitplane.

        :param bitplane: the bitplane to clear
        """
        if bitplane == 0:
            return

        if bitplane == 3:
            self.surface.fill(self.pixel_colors[0])
            return

        max_x = self.get_width()
        max_y = self.get_height()
        for x in range(max_x):
            for y in range(max_y):
                self.draw_pixel(x, y, False, bitplane)

    @staticmethod
    def update():
        """
        Updates the display by swapping the back buffer and screen buffer.
        According to the pygame documentation, the flip should wait for a
        vertical retrace when both HWSURFACE and DOUBLEBUF are set on the
        surface.
        """
        display.flip()

    def set_extended(self):
        """
        Sets the screen mode to extended.
        """
        self.mode = SCREEN_MODE_EXTENDED

    def set_normal(self):
        """
        Sets the screen mode to normal.
        """
        self.mode = SCREEN_MODE_NORMAL

    def scroll_down(self, num_lines, bitplane):
        """
        Scroll the screen down by num_lines.

        :param num_lines: the number of lines to scroll down
        :param bitplane: the bitplane to scroll
        """
        if bitplane == 0:
            return

        mode_scale = 1 if self.mode == SCREEN_MODE_EXTENDED else 2
        actual_lines = num_lines * mode_scale * self.scale_factor
        if bitplane == 3:
            self.surface.scroll(0, actual_lines)
            self.surface.fill(self.pixel_colors[0], (0, 0, self.width * mode_scale * self.scale_factor, actual_lines))
            self.update()
            return

        max_x = self.get_width()
        max_y = self.get_height()

        # Blank out any pixels in the bottom n lines that we will copy to
        for x in range(max_x):
            for y in range(max_y - num_lines, max_y):
                self.draw_pixel(x, y, False, bitplane)

        # Start copying pixels from the top to the bottom and shift by n pixels
        for x in range(max_x):
            for y in range(max_y - num_lines - 1, -1, -1):
                current_pixel = self.get_pixel(x, y, bitplane)
                self.draw_pixel(x, y, False, bitplane)
                self.draw_pixel(x, y + num_lines, current_pixel, bitplane)

        # Blank out any pixels in the first num_lines horizontal lines
        for x in range(max_x):
            for y in range(num_lines):
                self.draw_pixel(x, y, False, bitplane)

    def scroll_up(self, num_lines, bitplane):
        """
        Scroll the screen up by num_lines.

        :param num_lines: the number of lines to scroll up
        :param bitplane: the bitplane to scroll
        """
        if bitplane == 0:
            return

        mode_scale = 1 if self.mode == SCREEN_MODE_EXTENDED else 2
        actual_lines = num_lines * mode_scale * self.scale_factor
        if bitplane == 3:
            self.surface.scroll(0, -actual_lines)
            self.surface.fill(
                self.pixel_colors[0],
                (
                    0,
                    self.height * mode_scale * self.scale_factor - actual_lines,
                    self.width * mode_scale * self.scale_factor,
                    self.height * mode_scale * self.scale_factor
                )
            )
            self.update()
            return

        max_x = self.get_width()
        max_y = self.get_height()

        # Blank out any pixels in the top n lines that we will copy to
        for x in range(max_x):
            for y in range(num_lines):
                self.draw_pixel(x, y, False, bitplane)

        # Start copying pixels from the top to the bottom and shift up by n pixels
        for x in range(max_x):
            for y in range(num_lines, max_y):
                current_pixel = self.get_pixel(x, y, bitplane)
                self.draw_pixel(x, y, False, bitplane)
                self.draw_pixel(x, y - num_lines, current_pixel, bitplane)

        # Blank out any pixels in the bottom num_lines horizontal lines
        for x in range(max_x):
            for y in range(max_y - num_lines, max_y):
                self.draw_pixel(x, y, False, bitplane)

    def scroll_left(self, bitplane):
        """
        Scroll the screen left 4 pixels.

        :param bitplane: the bitplane to scroll
        """
        if bitplane == 0:
            return
        
        other_bitplane = 1 if bitplane == 2 else 2
        max_x = self.get_width()
        max_y = self.get_height()

        if bitplane == 3:
            # Blank out any pixels in the left 4 vertical lines that we will copy to
            for x in range(4):
                for y in range(max_y):
                    self.draw_pixel(x, y, False, 1)
                    self.draw_pixel(x, y, False, 2)

            # Start copying pixels from the right to the left and shift by 4 pixels
            for x in range(4, max_x):
                for y in range(max_y):
                    current_pixel = self.get_pixel(x, y, 1)
                    self.draw_pixel(x, y, False, 1)
                    self.draw_pixel(x - 4, y, current_pixel, 1)
                    current_pixel = self.get_pixel(x, y, 2)
                    self.draw_pixel(x, y, False, 2)
                    self.draw_pixel(x - 4, y, current_pixel, 2)

            # Blank out any pixels in the right 4 vertical lines
            for x in range(max_x - 4, max_x):
                for y in range(max_y):
                    self.draw_pixel(x, y, False, 1)
                    self.draw_pixel(x, y, False, 2)
        else:
            for x in range(4):
                for y in range(max_y):
                    self.draw_pixel(x, y, False, bitplane)

            # Start copying pixels from the right to the left and shift by 4 pixels
            for x in range(4, max_x):
                for y in range(max_y):
                    current_pixel = self.get_pixel(x, y, bitplane)
                    self.draw_pixel(x, y, False, bitplane)
                    self.draw_pixel(x - 4, y, current_pixel, bitplane)

            # Blank out any pixels in the right 4 vertical lines
            for x in range(max_x - 4, max_x):
                for y in range(max_y):
                    self.draw_pixel(x, y, False, bitplane)
        self.update()

    def scroll_right(self, bitplane):
        """
        Scroll the screen right 4 pixels.

        :param bitplane: the bitplane to scroll
        """
        if bitplane == 0:
            return

        mode_scale = 1 if self.mode == SCREEN_MODE_EXTENDED else 2
        actual_lines = 4 * mode_scale * self.scale_factor

        if bitplane == 3:
            self.surface.scroll(actual_lines, 0)
            self.surface.fill(self.pixel_colors[0], (0, 0, actual_lines, self.height * mode_scale * self.scale_factor))
            self.update()
            return

        max_x = self.get_width()
        max_y = self.get_height()

        # Blank out any pixels in the right vertical lines that we will copy to
        for x in range(max_x - 4, max_x):
            for y in range(max_y):
                self.draw_pixel(x, y, False, bitplane)

        # Start copying pixels from the left to the right and shift by 4 pixels
        for x in range(max_x - 4 - 1, -1, -1):
            for y in range(max_y):
                current_pixel = self.get_pixel(x, y, bitplane)
                self.draw_pixel(x, y, False, bitplane)
                self.draw_pixel(x + 4, y, current_pixel, bitplane)

        # Blank out any pixels in the left 4 vertical lines
        for x in range(4):
            for y in range(max_y):
                self.draw_pixel(x, y, False, bitplane)

# E N D   O F   F I L E ########################################################

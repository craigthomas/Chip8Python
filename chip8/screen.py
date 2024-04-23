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

# The colors of the pixels to draw. The Chip 8 supports two colors: 0 (off)
# and 1 (on). The format of the colors is in RGBA format.
PIXEL_COLORS = {
    0: Color(0, 0, 0, 255),
    1: Color(250, 250, 250, 255)
}

# C L A S S E S ###############################################################


class Chip8Screen:
    """
    A class to emulate a Chip 8 Screen. The original Chip 8 screen was 64 x 32
    with 2 colors. In this emulator, this translates to color 0 (off) and color
    1 (on).
    """
    def __init__(self, scale_factor):
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
        self.clear_screen()
        self.update()

    def draw_pixel(self, x_pos, y_pos, turn_on):
        """
        Turn a pixel on or off at the specified location on the screen. Note
        that the pixel will not automatically be drawn on the screen, you
        must call the update() function to flip the drawing buffer to the
        display. The coordinate system starts with (0, 0) being in the top
        left of the screen.

        :param x_pos: the x coordinate to place the pixel
        :param y_pos: the y coordinate to place the pixel
        :param turn_on: whether to turn the pixel on or off
        """
        mode_scale = 1 if self.mode == SCREEN_MODE_EXTENDED else 2
        pixel_color = 1 if turn_on else 0
        x_base = (x_pos * mode_scale) * self.scale_factor
        y_base = (y_pos * mode_scale) * self.scale_factor
        draw.rect(self.surface,
                  PIXEL_COLORS[pixel_color],
                  (x_base, y_base, mode_scale * self.scale_factor, mode_scale * self.scale_factor))

    def get_pixel(self, x_pos, y_pos):
        """
        Returns whether the pixel is on (1) or off (0) at the specified
        location.

        :param x_pos: the x coordinate to check
        :param y_pos: the y coordinate to check
        :return: true if the pixel is currently turned on
        """
        mode_scale = 1 if self.mode == SCREEN_MODE_EXTENDED else 2
        x_scale = (x_pos * mode_scale) * self.scale_factor
        y_scale = (y_pos * mode_scale) * self.scale_factor
        pixel_color = self.surface.get_at((x_scale, y_scale))
        return pixel_color == PIXEL_COLORS[1]

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

    def clear_screen(self):
        """
        Turns off all the pixels on the screen (writes color 0 to all pixels).
        """
        self.surface.fill(PIXEL_COLORS[0])

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

    def scroll_down(self, num_lines):
        """
        Scroll the screen down by num_lines.

        :param num_lines: the number of lines to scroll down
        """
        mode_scale = 1 if self.mode == SCREEN_MODE_EXTENDED else 2
        actual_lines = num_lines * mode_scale * self.scale_factor
        self.surface.scroll(0, actual_lines)
        self.surface.fill(PIXEL_COLORS[0], (0, 0, self.width * mode_scale * self.scale_factor, actual_lines))
        self.update()

    def scroll_left(self):
        """
        Scroll the screen left 4 pixels.
        """
        mode_scale = 1 if self.mode == SCREEN_MODE_EXTENDED else 2
        actual_lines = 4 * mode_scale * self.scale_factor
        left = (self.width * mode_scale * self.scale_factor) - actual_lines
        self.surface.scroll(-actual_lines, 0)
        self.surface.fill(PIXEL_COLORS[0], (left, 0, actual_lines, self.height * mode_scale * self.scale_factor))
        self.update()

    def scroll_right(self):
        """
        Scroll the screen right 4 pixels.
        """
        mode_scale = 1 if self.mode == SCREEN_MODE_EXTENDED else 2
        actual_lines = 4 * mode_scale * self.scale_factor
        self.surface.scroll(actual_lines, 0)
        self.surface.fill(PIXEL_COLORS[0], (0, 0, actual_lines, self.height * mode_scale * self.scale_factor))
        self.update()

# E N D   O F   F I L E ########################################################

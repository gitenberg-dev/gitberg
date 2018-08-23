#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python Implementation of the TenPrint Cover Processing script. For more information
and background see: http://www.nypl.org/blog/2014/09/03/generative-ebook-covers
This file is MIT licensed and maintained at https://github.com/mgiraldo/tenprintcover-py
"""

#
# Disable a few pylint warnings: the handling of variables and function names
# intentionally follows the original Processing source code, instead of the
# Python conventions.
#
# pylint: disable=invalid-name,too-many-arguments
#

#
# Python 2 truncates integer division to integer, whereas Python 3 turns the
# result of an integer division into a float. To ensure compatibility across
# the versions, import the correct division operator. See also PEP 238 and
# https://docs.python.org/2/library/__future__.html
#

from __future__ import division
from __future__ import print_function

import argparse
import itertools
import json
import math
import os
import sys

import cairocffi as cairo

PY2 = sys.version_info[0] == 2
if PY2:
    FileNotFoundError = IOError
#
# Private helper functions.
#

def _join(s, tail):
    """
    Return the concatenation of s + ' ' + tail if s is a truthy string, or tail
    only otherwise.
    """
    return " ".join((s, tail)) if s else tail

#
# The Image class wraps Cairo functionality into a Processing inspired interface.
#

class Image(object):
    """
    The Image class is a composition of different modules from Python's Cairo
    bindings. For more documentation on the use of Cairo and the Python bindings
    see here:

      https://github.com/SimonSapin/cairocffi
      http://cairographics.org/pycairo/ (outdated)

    Furthermore, instances of this class provide functions that resemble the
    original Processing functions and map them to Cairo functions. That makes
    porting the original Processing code easier.
    """

    def __init__(self, width, height):
        """
        Constructor. Create a Cairo image surface and a render context, and disables
        anti-aliasing for the image to keep the lines sharp.
        """
        self.width = width
        self.height = height
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.context = cairo.Context(self.surface)
        self.context.scale(width, height)
        self.context.set_antialias(cairo.ANTIALIAS_NONE)


    def tx(self, x):
        """
        Transform the given X coordinate from a pixel value [0..width] to a
        Cairo coordinate [0..1].
        """
        return x / self.width


    def ty(self, y):
        """
        Transform the given Y coordinate from a pixel value [0..height] to a
        Cairo coordinate [0..1].
        """
        return y / self.height


    def triangle(self, x1, y1, x2, y2, x3, y3, color):
        """
        See the Processing function triangle():
        https://processing.org/reference/triangle_.html
        """
        self.context.set_source_rgb(*color)
        self.context.move_to(self.tx(x1), self.ty(y1))
        self.context.line_to(self.tx(x2), self.ty(y2))
        self.context.line_to(self.tx(x3), self.ty(y3))
        self.context.line_to(self.tx(x1), self.ty(y1))
        self.context.fill()


    def rect(self, x, y, width, height, color):
        """
        See the Processing function rect():
        https://processing.org/reference/rect_.html
        """
        self.context.set_source_rgb(*color)
        self.context.rectangle(self.tx(x), self.ty(y), self.tx(width), self.ty(height))
        self.context.fill()


    def ellipse(self, x, y, width, height, color):
        """
        See the Processing function ellipse():
        https://processing.org/reference/ellipse_.html
        """
        self.context.set_source_rgb(*color)
        self.context.save()
        self.context.translate(self.tx(x + (width / 2.0)), self.ty(y + (height / 2.0)))
        self.context.scale(self.tx(width / 2.0), self.ty(height / 2.0))
        self.context.arc(0.0, 0.0, 1.0, 0.0, 2 * math.pi)
        self.context.fill()
        self.context.restore()


    def arc(self, x, y, width, height, start, end, color, thick=1, _=None):
        """
        This is different than the Processing function arc():
        https://processing.org/reference/arc_.html

        Use the Cairo arc() function to draw an arc with a given line thickness.
        """
        thick *= 4
        self.context.set_source_rgb(*color)
        self.context.save()
        self.context.translate(self.tx(x+(width/2)), self.ty(y+(height/2)))
        self.context.scale(self.tx(width/2), self.ty(height/2))
        self.context.arc(0.0, 0.0, 1.0 - (self.tx(thick)/2),
            (2*math.pi*start)/360,
            (2*math.pi*end)/360
        )
        self.context.set_line_width(self.tx(thick))
        self.context.stroke()
        self.context.restore()


    def text(self, text, x, y, width, height, color, font):
        """
        See the Processing function text():
        https://processing.org/reference/text_.html

        Consider using Pango in addition to Cairo here.
        """
        # Helper function.
        def chop(word):
            """
            Take a word longer than the bounding box's width and chop off as many
            letters in the beginning as fit, followed by an ellipsis.
            """
            total_str = ""
            for c in word:
                _, _, total_width, _, _, _ = self.context.text_extents(total_str + c + "…")
                if total_width >= width:
                    return total_str + "…"
                total_str += c
            assert not "Should not be here, else 'word' fit into the bounding box"
        # Prepare the context for text rendering.
        self.context.set_source_rgb(*color)
        font_name, (font_size, font_slant, font_weight) = (font)
        self.context.select_font_face(font_name, font_slant, font_weight)
        self.context.set_font_size(font_size)
        self.context.set_antialias(cairo.ANTIALIAS_DEFAULT)
        # Get some font metrics.
        font_asc, _, font_height, _, _ = self.context.font_extents()
        # Initialize text cursor to the baseline of the font.
        width, height = self.tx(width), self.ty(height)
        w_x, w_y = self.tx(x), font_asc + self.ty(y)
        # Draw the text one line at a time and ensure the bounding box.
        line = ""
        nlines = 1
        for word in text.split(" "):
            _, _, line_width, _, _, _ = self.context.text_extents(_join(line, word))
            if line_width < width:
                line = _join(line, word)
            else:
                if not line:
                    # First word of the line extends beyond the line: chop and done.
                    self.context.move_to(w_x, w_y)
                    self.context.show_text(chop(word))
                    return nlines, font_height
                else:
                    # Filled a line, render it, and move on to the next line.
                    self.context.move_to(w_x, w_y)
                    self.context.show_text(line)
                    line = word
                    w_y += font_height

                    if w_y > height:
                        return nlines, font_height
                    nlines += 1
        self.context.move_to(w_x, w_y)
        self.context.show_text(line)
        return nlines, font_height


    def save(self, filename=None):
        """
        Save this Image instance as PNG to the given filename. It is assumed
        that the filename extension is .png!
        """
        return self.surface.write_to_png(filename)


    def font(self, name, properties):
        """
        Return a tuple that contains font properties required for rendering.
        """
        size, slant, weight = (properties)
        return (name, (self.ty(size), slant, weight))


    @staticmethod
    def colorHSB(h, s, b):
        """
        Given the H,S,B (equivalent to H,S,V) values for the HSB color mode,
        convert them into the R,G,B values for the RGB color mode and return a
        color tuple. This conversion is necessary because Cairo understands
        only RGB(A).
        """
        H, S, B = float(h), float(s/100), float(b/100)
        if S == 0.0:
            return (B, B, B) # achromatic (grey)
        h = H / 60
        i = math.floor(h)
        f = h - i
        v = B
        p = v * (1 - S)
        q = v * (1 - S * f)
        t = v * (1 - S * (1 - f))
        if i == 0:
            return (v, t, b)
        elif i == 1:
            return (q, v, p)
        elif i == 2:
            return (p, v, t)
        elif i == 3:
            return (p, q, v)
        elif i == 4:
            return (t, p, v)
        else: # i == 5 (or i == 6 for the case of H == 360)
            return (v, p, q)


    @staticmethod
    def colorRGB(r, g, b):
        """
        Given the R,G,B int values for the RGB color mode in the range [0..255],
        return a RGB color tuple with float values in the range [0..1].
        """
        return (float(r / 255), float(g / 255), float(b / 255))


#
# Private helper functions.
#

def _map(value, istart, istop, ostart, ostop):
    """
    Helper function that implements the Processing function map(). For more
    details see https://processing.org/reference/map_.html
    http://stackoverflow.com/questions/17134839/how-does-the-map-function-in-processing-work
    """
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))


def _clip(value, lower, upper):
    """
    Helper function to clip a given value based on a lower/upper bound.
    """
    return lower if value < lower else upper if value > upper else value


#
# The draw() function creates an Image instance and draws the cover. Returns
# an Image instance which is a composition of different Cairo functionality.
#

def draw(title, subtitle, author, cover_width=400, cover_height=600):
    """
    Main drawing function, which generates a cover of the given dimension and
    renders title, author, and graphics.
    """

    # Based on some initial constants and the title+author strings, generate a base
    # background color and a shape color to draw onto the background. Try to keep
    # these two colors somewhat compatible with each other by varying only their hue.
    def processColors():
        base_saturation = 100
        base_brightness = 90
        color_distance = 100
        invert = True

        counts = len(title) + len(author)
        color_seed = int(_map(_clip(counts, 2, 80), 2, 80, 10, 360))
        shape_color = Image.colorHSB(color_seed, base_saturation, base_brightness-(counts % 20))
        base_color = Image.colorHSB((
            color_seed + color_distance) % 360,
            base_saturation,
            base_brightness
        )
        if invert:
            shape_color, base_color = base_color, shape_color
        if (counts % 10) == 0:
            shape_color, base_color = base_color, shape_color
        return shape_color, base_color


    # Fill the background of the image with white.
    def drawBackground():
        fill = Image.colorRGB(255, 255, 255)
        cover_image.rect(0, 0, cover_width, cover_height, fill)


    # Draw the actual artwork for the cover. Given the length of the title string,
    # generate an appropriate sized grid and draw C64 PETSCII into each of the cells.
    # https://www.c64-wiki.com/index.php/PETSCII
    # https://en.wikipedia.org/wiki/PETSCII#/media/File:PET_Keyboard.svg
    def drawArtwork():
        artwork_start_x = 0
        artwork_start_y = cover_height - cover_width

        grid_count, grid_total, grid_size = breakGrid()
        cover_image.rect(0, 0, cover_width, cover_height * cover_margin / 100, base_color)
        cover_image.rect(0, 0 + artwork_start_y, cover_width, cover_width, base_color)
        c64_title = c64Convert()
        for c, i in zip(itertools.cycle(c64_title), range(0, grid_total)):
            grid_x = int(i % grid_count)
            grid_y = int(i / grid_count)
            x = grid_x * grid_size + artwork_start_x
            y = grid_y * grid_size + artwork_start_y
            drawShape(c, x, y, grid_size)


    # Compute the graphics grid size based on the length of the book title.
    def breakGrid():
        min_title = 2
        max_title = 60
        length = _clip(len(title), min_title, max_title)

        grid_count = int(_map(length, min_title, max_title, 2, 11))
        grid_total = grid_count * grid_count
        grid_size = cover_width / grid_count
        return grid_count, grid_total, grid_size


    # Given the title of the book, filter through its characters and ensure
    # that only a certain range is used for the title; characters outside of
    # that range are replaced with a somewhat random character.
    def c64Convert():
        c64_letters = " qQwWeErRtTyYuUiIoOpPaAsSdDfFgGhHjJkKlL:zZxXcCvVbBnNmM,;?<>@[]1234567890.=-+*/"
        c64_title = ""
        for c in title:
            if c in c64_letters:
                c64_title += c
            else:
                c64_title += c64_letters[ord(c) % len(c64_letters)]
        return c64_title


    # Given an alphabetic character from the book's title string and the x, y
    # coordinates and size of the cell within the cover grid, draw a PETSCII
    # shape into that cell.
    def drawShape(c, x, y, s):
        shape_thickness = 10
        thick = int(s * shape_thickness / 100)
        if c in "qQ":
            cover_image.ellipse(x, y, s, s, shape_color)
        elif c in "wW":
            cover_image.ellipse(x, y, s, s, shape_color)
            cover_image.ellipse(x+thick, y+thick, s-(thick*2), s-(thick*2), base_color)
        elif c in "eE":
            cover_image.rect(x, y+thick, s, thick, shape_color)
        elif c in "rR":
            cover_image.rect(x, y+s-(thick*2), s, thick, shape_color)
        elif c in "tT":
            cover_image.rect(x+thick, y, thick, s, shape_color)
        elif c in "yY":
            cover_image.rect(x+s-(thick*2), y, thick, s, shape_color)
        elif c in "uU":
            cover_image.arc(x, y, 2*s, 2*s, 180, 270, shape_color, thick)
        elif c in "iI":
            cover_image.arc(x-s, y, 2*s, 2*s, 270, 360, shape_color, thick)
        elif c in "oO":
            cover_image.rect(x, y, s, thick, shape_color)
            cover_image.rect(x, y, thick, s, shape_color)
        elif c in "pP":
            cover_image.rect(x, y, s, thick, shape_color)
            cover_image.rect(x+s-thick, y, thick, s, shape_color)
        elif c in "aA":
            cover_image.triangle(x, y+s, x+(s/2), y, x+s, y+s, shape_color)
        elif c in "sS":
            cover_image.triangle(x, y, x+(s/2), y+s, x+s, y, shape_color)
        elif c in "dD":
            cover_image.rect(x, y+(thick*2), s, thick, shape_color)
        elif c in "fF":
            cover_image.rect(x, y+s-(thick*3), s, thick, shape_color)
        elif c in "gG":
            cover_image.rect(x+(thick*2), y, thick, s, shape_color)
        elif c in "hH":
            cover_image.rect(x+s-(thick*3), y, thick, s, shape_color)
        elif c in "jJ":
            cover_image.arc(x, y-s, 2*s, 2*s, 90, 180, shape_color, thick)
        elif c in "kK":
            cover_image.arc(x-s, y-s, 2*s, 2*s, 0, 90, shape_color, thick)
        elif c in "lL":
            cover_image.rect(x, y, thick, s, shape_color)
            cover_image.rect(x, y+s-thick, s, thick, shape_color)
        elif c == ":":
            cover_image.rect(x+s-thick, y, thick, s, shape_color)
            cover_image.rect(x, y+s-thick, s, thick, shape_color)
        elif c in "zZ":
            cover_image.triangle(x, y+(s/2), x+(s/2), y, x+s, y+(s/2), shape_color)
            cover_image.triangle(x, y+(s/2), x+(s/2), y+s, x+s, y+(s/2), shape_color)
        elif c in "xX":
            cover_image.ellipse(x+(s/2), y+(s/3), thick*2, thick*2, shape_color)
            cover_image.ellipse(x+(s/3), y+s-(s/3), thick*2, thick*2, shape_color)
            cover_image.ellipse(x+s-(s/3), y+s-(s/3), thick*2, thick*2, shape_color)
        elif c in "cC":
            cover_image.rect(x, y+(thick*3), s, thick, shape_color)
        elif c in "vV":
            cover_image.rect(x, y, s, s, shape_color)
            cover_image.triangle(x+thick, y, x+(s/2), y+(s/2)-thick, x+s-thick, y, base_color)
            cover_image.triangle(x, y+thick, x+(s/2)-thick, y+(s/2), x, y+s-thick, base_color)
            cover_image.triangle(x+thick, y+s, x+(s/2), y+(s/2)+thick, x+s-thick, y+s, base_color)
            cover_image.triangle(x+s, y+thick, x+s, y+s-thick, x+(s/2)+thick, y+(s/2), base_color)
        elif c in "bB":
            cover_image.rect(x+(thick*3), y, thick, s, shape_color)
        elif c in "nN":
            cover_image.rect(x, y, s, s, shape_color)
            cover_image.triangle(x, y, x+s-thick, y, x, y+s-thick, base_color)
            cover_image.triangle(x+thick, y+s, x+s, y+s, x+s, y+thick, base_color)
        elif c in "mM":
            cover_image.rect(x, y, s, s, shape_color)
            cover_image.triangle(x+thick, y, x+s, y, x+s, y+s-thick, base_color)
            cover_image.triangle(x, y+thick, x, y+s, x+s-thick, y + s, base_color)
        elif c == ",":
            cover_image.rect(x+(s/2), y+(s/2), s/2, s/2, shape_color)
        elif c == ";":
            cover_image.rect(x, y+(s/2), s/2, s/2, shape_color)
        elif c == "?":
            cover_image.rect(x, y, s/2, s/2, shape_color)
            cover_image.rect(x+(s/2), y+(s/2), s/2, s/2, shape_color)
        elif c == "<":
            cover_image.rect(x+(s/2), y, s/2, s/2, shape_color)
        elif c == ">":
            cover_image.rect(x, y, s/2, s/2, shape_color)
        elif c == "@":
            cover_image.rect(x, y+(s/2)-(thick/2), s, thick, shape_color)
        elif c == "[":
            cover_image.rect(x+(s/2)-(thick/2), y, thick, s, shape_color)
        elif c == "]":
            cover_image.rect(x, y+(s/2)-(thick/2), s, thick, shape_color)
            cover_image.rect(x+(s/2)-(thick/2), y, thick, s, shape_color)
        elif c == "0":
            cover_image.rect(x+(s/2)-(thick/2), y+(s/2)-(thick/2), thick, s/2+thick/2, shape_color)
            cover_image.rect(x+(s/2)-(thick/2), y+(s/2)-(thick/2), s/2+thick/2, thick, shape_color)
        elif c == "1":
            cover_image.rect(x, y+(s/2)-(thick/2), s, thick, shape_color)
            cover_image.rect(x+(s/2)-(thick/2), y, thick, s/2+thick/2, shape_color)
        elif c == "2":
            cover_image.rect(x, y+(s/2)-(thick/2), s, thick, shape_color)
            cover_image.rect(x+(s/2)-(thick/2), y+(s/2)-(thick/2), thick, s/2+thick/2, shape_color)
        elif c == "3":
            cover_image.rect(x, y+(s/2)-(thick/2), s/2+thick/2, thick, shape_color)
            cover_image.rect(x+(s/2)-(thick/2), y, thick, s, shape_color)
        elif c == "4":
            cover_image.rect(x, y, thick*2, s, shape_color)
        elif c == "5":
            cover_image.rect(x, y, thick*3, s, shape_color)
        elif c == "6":
            cover_image.rect(x+s-(thick*3), y, thick*3, s, shape_color)
        elif c == "7":
            cover_image.rect(x, y, s, thick*2, shape_color)
        elif c == "8":
            cover_image.rect(x, y, s, thick*3, shape_color)
        elif c == "9":
            cover_image.rect(x, y+s-(thick*3), s, thick*3, shape_color)
        elif c == ".":
            cover_image.rect(x+(s/2)-(thick/2), y+(s/2)-(thick/2), thick, s/2+thick/2, shape_color)
            cover_image.rect(x, y+(s/2)-(thick/2), s/2+thick/2, thick, shape_color)
        elif c == "=":
            cover_image.rect(x+(s/2)-(thick/2), y, thick, s/2+thick/2, shape_color)
            cover_image.rect(x, y+(s/2)-(thick/2), s/2, thick, shape_color)
        elif c == "-":
            cover_image.rect(x+(s/2)-(thick/2), y, thick, s/2+thick/2, shape_color)
            cover_image.rect(x+(s/2)-(thick/2), y+(s/2)-(thick/2), s/2+thick/2, thick, shape_color)
        elif c == "+":
            cover_image.rect(x+(s/2)-(thick/2), y+(s/2)-(thick/2), s/2+thick/2, thick, shape_color)
            cover_image.rect(x+(s/2)-(thick/2), y, thick, s, shape_color)
        elif c == "*":
            cover_image.rect(x+s-(thick*2), y, thick*2, s, shape_color)
        elif c == "/":
            cover_image.rect(x, y+s-(thick*2), s, thick*2, shape_color)
        elif c == " ":
            cover_image.rect(x, y, s, s, base_color)
        else:
            assert not "Implement."

    # If the text is long, use a smaller font size.
    def scale_font(text, font_name, font_properties):
        (font_size, font_slant, font_weight) = font_properties
        w = len(text) * font_size
        if w > cover_width * 3:   #This is an empirical, unintelligent, heuristic.
            return  (font_size * 0.8, font_slant, font_weight)
        elif w < cover_width :
            return  (font_size * 1.2, font_slant, font_weight)
        else:
            return font_properties

    # return a font appropriate for the text. Uses Noto CJK if text contains CJK, otherwise
    # Noto Sans.
    
    def select_font(text):
        for char in text:
            if ord(char) >= 0x4E00:
                return 'Noto Sans CJK SC'
        return 'Noto Sans'

    # Allocate fonts for the title and the author, and draw the text.
    
    def drawText():
        fill = Image.colorRGB(50, 50, 50)

        title_font_size = cover_width * 0.08
        subtitle_font_size = cover_width * 0.05
        title_font_properties = (title_font_size, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        subtitle_font_properties = (subtitle_font_size, cairo.FONT_SLANT_NORMAL,
                                     cairo.FONT_WEIGHT_NORMAL)
        title_font_family = select_font(title)
        subtitle_font_family = select_font(subtitle)
        title_font_properties = scale_font(title, title_font_family, title_font_properties)
        subtitle_font_properties = scale_font(
            subtitle,
            subtitle_font_family,
            subtitle_font_properties
        )
        title_font = cover_image.font(title_font_family, title_font_properties)
        subtitle_font = cover_image.font(subtitle_font_family, subtitle_font_properties)
        title_height = (cover_height - cover_width - (cover_height * cover_margin / 100)) * 0.75

        x = cover_height * cover_margin / 100
        y = cover_height * cover_margin / 100 * 2
        width = cover_width - (2 * cover_height * cover_margin / 100)
        height = title_height
        title_lines, font_height = cover_image.text(title, x, y, width, height, fill, title_font)
        if subtitle:
            y = min(
                y + font_height * title_lines * cover_height,
                title_height - subtitle_font_properties[0]
            )

            cover_image.text(subtitle, x, y, width, height, fill, subtitle_font)

        author_font_size = cover_width * 0.07
        author_font_properties = (
            author_font_size,
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL
        )
        author_font = cover_image.font(select_font(author), author_font_properties)
        author_height = (cover_height - cover_width - (cover_height * cover_margin / 100)) * 0.25
        x = cover_height * cover_margin / 100
        y = title_height
        width = cover_width - (2 * cover_height * cover_margin / 100)
        height = author_height
        cover_image.text(author, x, y, width, height, fill, author_font)

    # Create the new cover image.
    cover_margin = 2
    cover_image = Image(cover_width, cover_height)

    # Draw the book cover.
    shape_color, base_color = processColors()
    drawBackground()
    drawArtwork()
    drawText()

    # Return the cover Image instance.
    return cover_image


#
# The main function allows to run the cover generation to run as a standalone
# command-line tool. Arguments can be passed, use -h or --help to get a list
# of available switches. The generated book cover is saved as an image file.
#

def main():
    """
    The main() function handles command line arguments and maneuvers the cover
    image generation.
    """
    # Helper function.
    def _draw_and_save(title, subtitle, author, filename):
        """
        Draw a cover and write it to a file. Note that only PNG is supported.
        """
        cover_image = draw(title, subtitle, author)
        if filename == "-":
            assert not "Implement."
        else:
            _, ext = os.path.splitext(os.path.basename(filename))
            if ext.upper() == ".PNG":
                try:
                    with open(filename, "wb") as f:
                        cover_image.save(f)
                except FileNotFoundError:
                    print("Error opening target file " + filename)
                    return 1
            else:
                print("Unsupported image file format '" + ext + "', use PNG")
                return 1
        return 0

    # Set up and parse the command line arguments passed to the program.
    usage = "Python implementation of the 10PRINT Cover image generator."
    parser = argparse.ArgumentParser(usage=usage)

    parser.add_argument("-t", "--title", dest="title", help="Book title")
    parser.add_argument("-s", "--subtitle", dest="subtitle", help="Book subtitle", default="")
    parser.add_argument("-a", "--author", dest="author", help="Author(s) of the book")
    parser.add_argument("-o", "--cover", dest="outfile", help="Filename of the cover image in PNG format")
    parser.add_argument("-j", "--json-covers", dest="json_covers", help="JSON file containing cover information")
    args = parser.parse_args()

    # A JSON file is given as command line parameter; ignore the other ones.
    # Read the file line by line and use the given information to generate the
    # book covers. The file contains lines of JSON maps of the format
    #
    #   {"authors": "..", "identifier": "..", "subtitle": null, "title": "..",
    #    "identifier_type": "Gutenberg ID", "filename": ".."}
    if args.json_covers:
        try:
            with open(args.json_covers, "r") as f:
                for line in f:
                    data = json.loads(line)
                    print("Generating cover for " + data["identifier"])
                    status = _draw_and_save(
                        data["title"],
                        data["subtitle"],
                        data["authors"],
                        data["filename"]
                    )
                    if status:
                        print("Error generating book cover image, skipping")
            return 0
        except ValueError:
            print("Error reading from JSON file, exiting")
        except FileNotFoundError:
            print("JSON cover file does not exist: " + args.json_covers)

    # Generate only a single cover based on the given command line arguments.
    else:
        if not args.title or not args.author:
            print("Missing --title or --author argument, exiting")
        elif not args.outfile:
            print("No outfile specified, exiting")
        else:
            return _draw_and_save(args.title, args.subtitle, args.author, args.outfile)
    return 1


#
# When run standalone, invoke the main() function here.
#

if __name__ == "__main__":
    sys.exit(main())

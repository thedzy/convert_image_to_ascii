#!/usr/bin/env python3

"""
Script:	convert_image_to_ascii.py
Date:	2020-04-24

Platform: MacOS/Windows/Linux

Description:
Convert an image to ascii
"""
__author__ = 'thedzy'
__copyright__ = 'Copyright 2020, thedzy'
__license__ = 'GPL'
__version__ = '1.0'
__maintainer__ = 'thedzy'
__email__ = 'thedzy@hotmail.com'
__status__ = 'Developer'

import argparse
import os

from PIL import Image, ImageFont, ImageDraw, ImageStat


def main():
    # Get image path of file
    image_name = options.image_file.name
    options.image_file.close()

    # Create shader
    if options.characters is not None:
        # Filter out duplicates
        characters = list(set(options.characters))

        # Load font to be used
        font = ImageFont.truetype(options.font.name, 18)
        options.font.close()

        # Get average brightness of a character
        character_values = {}
        for character in characters:
            character_image = Image.new('L', (10, 20), 0)
            draw = ImageDraw.Draw(character_image)
            draw.text((0, 0), character, font=font, fill=255, align='center')
            image_mean = ImageStat.Stat(character_image).mean[0]
            character_values[character] = image_mean

        # Sort the values into an array
        shader = []
        while len(character_values) > 0:
            key = min(character_values, key=character_values.get)
            shader.append(key)
            del character_values[key]
    else:
        shader = list(options.shader)
    shader_length = len(shader) - 1

    # Invert if black on white
    if options.black_on_white:
        shader = shader[::-1]


    # Load image
    image = Image.open(image_name)

    # Get dimension but skip entirely if using custom settings
    if options.custom_width is None or options.custom_height is None:
        window_width, window_height = os.get_terminal_size()
    image_width, image_height = image.size

    # Allow override of dimensions
    if options.custom_width is not None:
        window_width = options.custom_width
    if options.custom_height is not None:
        window_height = options.custom_height

    # Get rations to find out how to scale the image
    window_ratio = (window_width / options.aspect) / window_height
    image_ratio = image_width / image_height

    # Calculate new sizes
    if window_ratio > image_ratio:
        new_height = window_height
        new_width = int((window_height / image_height) * image_width * options.aspect)
    else:
        new_height = int((window_width / image_width) * image_height / options.aspect)
        new_width = window_width

    # Resize image
    image = image.resize((new_width, new_height))

    # Get pixel data in RGB
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image_data = image.getdata()

    # Break image into a matrix of perceived values
    image_matrix = []
    for x in range(new_width):
        row = []
        for y in range(new_height):
            image_pixel = image_data.getpixel((x, y))
            image_contrast = int(colour_contrast_rgb(image_pixel[0], image_pixel[1], image_pixel[2]) * shader_length)
            row.append(image_contrast)
        image_matrix.append(row)

    # Write data out
    file_data = ''
    for y in range(new_height):
        for x in range(new_width):
            file_data += shader[image_matrix[x][y]]
        file_data += '\n'

    # Print and/or save
    print(file_data)
    if options.out_file is not None:
        options.out_file.write(file_data)
        options.out_file.close()


def colour_contrast_rgb(red, green, blue):
    """
    Calculate the perceived bright of a pixel
    (ie, Full yellow is perceived brighter than full blue)
    :param red: (int) 0-255
    :param green: (int) 0-255
    :param blue: (int) 0-255
    :return: (float) 0-1
    """
    colour_value = ((red * 299) + (green * 587) + (blue * 114)) / 255000
    return colour_value


if __name__ == '__main__':

    def parser_formatter(format_class, **kwargs):
        """
        Use a raw parser to use line breaks, etc
        :param format_class: (class) formatting class
        :param kwargs: (dict) kwargs for class
        :return: (class) formatting class
        """
        try:
            return lambda prog: format_class(prog, **kwargs)
        except TypeError:
            return format_class

    parser = argparse.ArgumentParser(description='Convert image to ascii',
                                     formatter_class=parser_formatter(
                                         argparse.RawTextHelpFormatter,
                                         indent_increment=4, max_help_position=12, width=160))

    # Image file to read in
    parser.add_argument('-i', '--image', type=argparse.FileType('r'),
                        action='store', dest='image_file', default=None,
                        help='Image file to use'
                             '\nDefault: %(default)s',
                        required=True)

    # Text file to create
    parser.add_argument('-o', '--out-file', type=argparse.FileType('w'),
                        action='store', dest='out_file', default=None,
                        help='Text file to write'
                             '\nDefault: %(default)s',
                        required=False)

    # Text of character to render from
    parser.add_argument('-s', '--shader', type=str,
                        action='store', dest='shader',
                        default=' .\'`^",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$',
                        help='Dark to light characters to use'
                             '\nDefault: %(default)s')

    # Text of character to render from
    parser.add_argument('-c', '--chars', type=str,
                        action='store', dest='characters', default=None,
                        help='Dark to light characters to use\n'
                             'Overrides -s/--shader')
    parser.add_argument('-f', '--font', type=argparse.FileType('r'),
                        action='store', dest='font', default='/System/Library/Fonts/Menlo.ttc',
                        help='Font used to determine brightness when specifing characters\n'
                             'Required for non-macOS systems')

    # Custom width and heights
    parser.add_argument('-x', '--width', type=int,
                        action='store', dest='custom_width', default=None,
                        help='Custom width, recommended only for file output'
                             '\nDefault: Window width')
    parser.add_argument('-y', '--height', type=int,
                        action='store', dest='custom_height', default=None,
                        help='Custom height, recommended only for file output'
                             '\nDefault: Window height')

    # Character aspect ratio
    parser.add_argument('-a', '--char-aspect', type=int,
                        action='store', dest='aspect', default=2.4,
                        help='Aspect ratio of the character, ADVANCED'
                             '\nDefault: %(default)s'
                             'Adjust if aspect ration of the image feels off.  Height / width of a character block')

    # Black/white
    parser.add_argument('-b', '--black-on-white',
                        action='store_true', dest='black_on_white', default=False,
                        help='Terminal is using dark text on light background'
                             '\nDefault: %(default)s')

    options = parser.parse_args()

    main()

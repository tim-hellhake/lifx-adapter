"""Utility functions."""

import colorsys


def hsv_to_rgb(h, s, v):
    """
    Convert an HSV tuple to an RGB hex string.

    h -- hue (0-65535)
    s -- saturation (0-65535)
    v -- value (0-65535)

    Returns a hex RGB string, i.e. #123456.
    """
    r, g, b = tuple(int(i * 255)
                    for i in colorsys.hsv_to_rgb(h / 65535.0,
                                                 s / 65535.0,
                                                 v / 65535.0))
    return '#{:02X}{:02X}{:02X}'.format(r, g, b)


def rgb_to_hsv(rgb):
    """
    Convert an RGB hex string to an HSV tuple.

    rgb -- RGB hex string, i.e. #123456

    Returns an HSV tuple, i.e. (65535, 65535, 65535).
    """
    rgb = rgb.lstrip('#')
    r, g, b = tuple(int(rgb[i:i + 2], 16) / 255 for i in range(0, 6, 2))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return (int(h * 65535.0), int(s * 65535.0), int(v * 65535.0))

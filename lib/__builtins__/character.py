#!/usr/bin/env python

"""
Character-related functions.

Copyright (C) 2015, 2016, 2017 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __builtins__.types import check_int, check_string
from native import str_chr, str_ord

def chr(i):

    "Return a string containing a character having the value 'i'."

    check_int(i)

    if 0 <= i <= 255:
        return str_chr(i.__data__)
    else:
        raise ValueError, i

_hexdigits = "0123456789abcdef"

def _base(number, base, prefix=""):

    """
    Return 'number' encoded in the given 'base', prefixed with 'prefix'.
    """

    if number < 0:
        number = -number
        sign = "-"
    else:
        sign = ""

    digits = []

    if number:
        while number:
            digits.append(_hexdigits[number % base])
            number = number / base
    else:
        digits.append("0")

    digits.append(prefix)

    if sign:
        digits.append(sign)

    return "".join(reversed(digits))

def hex(number, prefix="0x"):

    """
    Return 'number' encoded as a hexadecimal (base 16) value, prefixed with
    'prefix' ("0x" by default).
    """

    return _base(number, 16, prefix)

def oct(number, prefix="0"):

    """
    Return 'number' encoded as an octal (base 8) value, prefixed with 'prefix'
    ("0" by default).
    """

    return _base(number, 8, prefix)

def ord(c):

    "Return the value of the given character 'c'."

    check_string(c)

    if c.__len__() == 1:
        return str_ord(c.__data__)
    else:
        raise ValueError, c

def unichr(i): pass

# vim: tabstop=4 expandtab shiftwidth=4

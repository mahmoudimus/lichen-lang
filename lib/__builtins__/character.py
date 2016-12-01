#!/usr/bin/env python

"""
Character-related functions.

Copyright (C) 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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

from native import _str_ord

def chr(i): pass
def hex(number): pass
def oct(number): pass

def ord(c):

    "Return the value of the given character 'c'."

    if isinstance(c, string) and len(c) == 1:
        return _str_ord(c)
    else:
        raise ValueError(c)

def unichr(i): pass

# vim: tabstop=4 expandtab shiftwidth=4

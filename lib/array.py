#!/usr/bin/env python

"""
Array functions and objects.

Copyright (C) 2011, 2014 Paul Boddie <paul@boddie.org.uk>

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

class array:

    """
    An array of primitive objects.
    NOTE: In principle, arrays of full instances could be supported with
    NOTE: knowledge of the size of each instance.
    """

    def __init__(self, typecode, itemsize):
        self.typecode = typecode
        self.itemsize = itemsize

    def append(self, value): pass
    def buffer_info(self): pass
    def byteswap(self): pass
    def count(self, value): pass
    def extend(self, l): pass
    def fromfile(self, f): pass
    def fromlist(self, l): pass
    def fromstring(self, s): pass
    def index(self, value): pass
    def insert(self, index, value): pass
    def pop(self): pass
    def read(self): pass
    def remove(self, value): pass
    def reverse(self): pass
    def tofile(self): pass
    def tolist(self): pass
    def tostring(self): pass
    def write(self): pass

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"""
Buffer object.

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

from native import _list_init, _list_append, _list_concat, _buffer_str

class buffer(object):

    "A buffer, used to build strings."

    def __init__(self, args=None, size=0):

        "Initialise a buffer from the given 'args' or the given 'size'."

        if args is not None:
            n = len(args)
        elif isinstance(size, int):
            n = size
        else:
            raise TypeError(size)

        self.__data__ = _list_init(n)

        # Append all arguments in string form to the buffer.

        if args:
            for arg in args:
                _list_append(self, str(arg))

    def append(self, s):

        "Append 's' to the buffer."

        if isinstance(s, buffer):
            _list_concat(self, s)
        elif isinstance(s, string):
            _list_append(self, s)
        else:
            raise TypeError(s)

    def __str__(self):

        "Return a string representation."

        return _buffer_str(self)

# vim: tabstop=4 expandtab shiftwidth=4

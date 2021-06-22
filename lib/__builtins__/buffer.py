#!/usr/bin/env python

"""
Buffer object.

Copyright (C) 2015, 2016, 2017, 2021 Paul Boddie <paul@boddie.org.uk>

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

from native import list_init, list_append, list_concat, buffer_str

class buffer:

    "A buffer, used to build strings."

    def __init__(self, args=None, size=0):

        "Initialise a buffer from the given 'args' or the given 'size'."

        if args is not None:
            n = len(args)
        elif isinstance(size, integer):
            n = size
        else:
            raise ValueError(size)

        self.__data__ = list_init(n)

        # Append all arguments to the buffer.

        if args:
            for arg in args:
                self.append(arg)

    def append(self, s):

        """
        Append 's' to the buffer, concatenating buffers and adding other objects
        in string form.
        """

        if isinstance(s, buffer):
            list_concat(self, s.__data__)
        elif isinstance(s, string):
            list_append(self, s)
        else:
            list_append(self, str(s))

    def __str__(self):

        "Return a string representation."

        return buffer_str(self.__data__)

    def __repr__(self):

        "Return a program representation."

        return buffer(["buffer([", repr(str(self)), "])"])

# vim: tabstop=4 expandtab shiftwidth=4

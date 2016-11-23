#!/usr/bin/env python

"""
Tuple objects.

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

from __builtins__.iterator import listiterator
from __builtins__.sequence import sequence
import native

class tuple(sequence):

    "Implementation of tuple."

    def __init__(self, args=None):

        "Initialise the tuple."

        # Reserve an attribute for a fragment reference along with some space
        # for elements.

        size = args is not None and len(args) or 0
        self.__data__ = native._list_init(size)
        native._list_setsize(self, size)

        # Populate the tuple.

        if args is not None:
            i = 0
            for arg in args:
                native._list_setelement(self, i, arg)
                i += 1

    def __getslice__(self, start, end=None):

        "Return a slice starting from 'start', with the optional 'end'."

        return tuple(get_using(sequence.__getslice__, self)(start, end))

    def __len__(self):

        "Return the length of the tuple."

        return native._list_len(self)

    def __add__(self, other): pass

    def __str__(self):

        "Return a string representation."

        return self._str("(", ")")

    __repr__ = __str__

    def __bool__(self):

        "Tuples are true if non-empty."

        return self.__len__() != 0

    def __iter__(self):

        "Return an iterator."

        return listiterator(self)

    # Special implementation methods.

    def __get_single_item__(self, index):

        "Return the item at the normalised (positive) 'index'."

        if index >= len(self):
            raise IndexError(index)

        return native._list_element(self, index)

    def __set_single_item__(self, index, value):

        "Set at the normalised (positive) 'index' the given 'value'."

        raise TypeError(self)

# vim: tabstop=4 expandtab shiftwidth=4

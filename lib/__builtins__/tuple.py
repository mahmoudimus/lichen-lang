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

        self.__data__ = native._tuple_init(args, len(args)) # allocate and copy elements

    def __getslice__(self, start, end=None):

        "Return a slice starting from 'start', with the optional 'end'."

        return native._list_to_tuple(get_using(sequence.__getslice__, self)(start, end))

    def __len__(self):

        "Return the length of the tuple."

        return native._tuple_len(self)

    def __add__(self, other): pass

    def __str__(self): pass

    __repr__ = __str__

    def __bool__(self):

        "Tuples are true if non-empty."

        return self.__len__() != 0

    def __iter__(self):

        "Return an iterator."

        return listiterator(self)

    # Special implementation methods.

    def __get_single_item__(self, index):
        return native._tuple_element(self, index)

# vim: tabstop=4 expandtab shiftwidth=4

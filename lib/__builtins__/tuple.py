#!/usr/bin/env python

"""
Tuple objects.

Copyright (C) 2015, 2016, 2017, 2018 Paul Boddie <paul@boddie.org.uk>

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

from __builtins__.iteration.iterator import itemiterator
from __builtins__.sequence import hashable, sequence
from native import tuple_init, \
                   list_element, list_len, list_setsize, list_setelement, \
                   isinstance as _isinstance

class tuple(sequence, hashable):

    "Implementation of tuple."

    def __init__(self, args=None):

        "Initialise the tuple."

        # Reserve an attribute for a fragment reference along with some space
        # for elements.

        if args is None:
            size = 0
        else:
            size = args.__len__()

        self.__data__ = tuple_init(size)

        if size:
            list_setsize(self.__data__, size)

            # Populate the tuple.

            i = 0
            while i < size:
                list_setelement(self.__data__, i, args[i])
                i += 1

    def __hash__(self):

        "Return a hashable value for the tuple."

        return self._hashvalue(hash)

    def __getslice__(self, start, end=None, step=1):

        """
        Return a slice starting from 'start', with the optional 'end' and
        'step'.
        """

        return tuple(get_using(sequence.__getslice__, self)(start, end, step))

    def __len__(self):

        "Return the length of the tuple."

        return list_len(self.__data__)

    def __add__(self, other):

        "Add this tuple to 'other'."

        if not _isinstance(other, tuple):
            raise TypeError
        return tuple(tuplepair(self, other))

    def __str__(self):

        "Return a string representation."

        return self._str("(", ")")

    __repr__ = __str__

    def __bool__(self):

        "Tuples are true if non-empty."

        return self.__len__() != 0

    def __iter__(self):

        "Return an iterator."

        return itemiterator(self)

    # Special implementation methods.

    def __get_single_item__(self, index):

        "Return the item at the normalised (positive) 'index'."

        self._check_index(index)
        return list_element(self.__data__, index)

    def __set_single_item__(self, index, value):

        "Set at the normalised (positive) 'index' the given 'value'."

        raise TypeError

class tuplepair:

    "A combination of tuples."

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __len__(self):

        "Return the combined length of the tuples."

        return len(self.a) + len(self.b)

    def __getitem__(self, index):

        "Return the value from 'index' in the combined tuple."

        asize = len(self.a)
        if index < asize:
            return self.a.__get_single_item__(index)
        else:
            return self.b.__get_single_item__(index - asize)

# vim: tabstop=4 expandtab shiftwidth=4

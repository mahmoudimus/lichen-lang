#!/usr/bin/env python

"""
List objects.

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

from __builtins__.iterator import itemiterator
from __builtins__.sequence import sequence
from native import list_append, list_concat, list_element, list_init, \
                   list_len, list_nonempty, list_setelement

class list(sequence):

    "Implementation of list."

    def __init__(self, args=None):

        "Initialise the list."

        # Reserve an attribute for a fragment reference along with some space
        # for elements.

        self.__data__ = list_init(args is not None and len(args) or 0)

        if args is not None:
            self.extend(args)

    def __delitem__(self, index): pass
    def __setslice__(self, start, end, slice): pass
    def __delslice__(self, start, end): pass

    def append(self, value):

        "Append 'value' to the list."

        list_append(self, value)

    def insert(self, i, value): pass

    def extend(self, iterable):

        "Extend the list with the contents of 'iterable'."

        for i in iterable:
            self.append(i)

    def pop(self): pass
    def reverse(self): pass
    def sort(self, cmp=None, key=None, reverse=0): pass

    def __len__(self):

        "Return the length of the list."

        return list_len(self.__data__)

    def __add__(self, other): pass

    def __iadd__(self, other):

        "Concatenate 'other' to the list."

        if isinstance(other, list):
            list_concat(self, other.__data__)
        else:
            self.extend(other)
        return self

    def __str__(self):

        "Return a string representation."

        return self._str("[", "]")

    __repr__ = __str__

    def __bool__(self):

        "Lists are true if non-empty."

        return list_nonempty(self.__data__)

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

        self._check_index(index)
        return list_setelement(self.__data__, index, value)

# vim: tabstop=4 expandtab shiftwidth=4

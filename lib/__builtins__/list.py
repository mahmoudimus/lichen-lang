#!/usr/bin/env python

"""
List objects.

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
from __builtins__.sequence import unpackable, _get_absolute_index
from native import list_append, list_concat, list_element, list_init, \
                   list_len, list_nonempty, list_setelement, list_setsize

class list(unpackable):

    "Implementation of list."

    def __init__(self, args=None):

        "Initialise the list."

        # Reserve an attribute for a fragment reference along with some space
        # for elements.

        self.__data__ = list_init(args is not None and len(args) or 0)

        if args is not None:
            self.extend(args)

    def __delitem__(self, index):

        "Delete the item at 'index'."

        length = self.__len__()
        index = _get_absolute_index(index, length)
        last = length - 1

        while index < last:
            self[index] = self[index + 1]
            index += 1

        # NOTE: Should truncate the allocated list after several pops.

        list_setsize(self.__data__, last)

    def __setslice__(self, start, end, slice): pass
    def __delslice__(self, start, end): pass

    def append(self, value):

        "Append 'value' to the list."

        list_append(self, value)

    def insert(self, index, value):

        "Insert at 'index' the given 'value'."

        length = self.__len__()
        index = _get_absolute_index(index, length)

        if index == length:
            self.append(value)
            return
        elif index > length:
            raise IndexError, index

        i = length - 1
        self.append(self.__getitem__(i))

        while i > index:
            self.__setitem__(i, self.__getitem__(i - 1))
            i -= 1

        self.__setitem__(index, value)

    def extend(self, iterable):

        "Extend the list with the contents of 'iterable'."

        for i in iterable:
            self.append(i)

    def pop(self):

        "Remove the last item from the list, returning the item."

        i = self[-1]

        # NOTE: Should truncate the allocated list after several pops.

        list_setsize(self.__data__, self.__len__() - 1)
        return i

    def reverse(self):

        "Reverse the list in-place."

        length = self.__len__()
        i = 0
        j = length - 1

        while i < j:
            item = self.__getitem__(j)
            self.__setitem__(j, self.__getitem__(i))
            self.__setitem__(i, item)
            i += 1
            j -= 1

    def sort(self, cmp=None, key=None, reverse=0): pass

    def __len__(self):

        "Return the length of the list."

        return list_len(self.__data__)

    def __add__(self, other):

        "Add this list to 'other', producing a new list."

        l = list(self)
        l.extend(other)
        return l

    def __iadd__(self, other):

        "Concatenate 'other' to the list."

        if isinstance(other, list):
            list_concat(self, other.__data__)
        else:
            self.extend(other)
        return self

    def __mul__(self, other):

        "Replicate this sequence 'other' times."

        return self._mul(list(self), other)

    def __imul__(self, other):

        "Replicate this list 'other' times."

        return self._mul(self, other)

    def _mul(self, l, other):

        "Replicate 'l' 'other' times."

        copy = list(self)
        while other > 1:
            l.extend(copy)
            other -= 1
        return l

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

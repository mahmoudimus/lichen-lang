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

from __builtins__.iterator import listiterator
from __builtins__.sequence import _getitem, _getslice
import native

class list(object):

    "Implementation of list."

    def __init__(self, args=None):

        "Initialise the list."

        # Reserve an attribute for a fragment reference along with some space
        # for elements.

        self.__data__ = native._list_init(len(args))

        if args is not None:
            self.extend(args)

    def __getitem__(self, index):

        "Return the item or slice specified by 'index'."

        return _getitem(self, index)

    def __contains__(self, value): pass
    def __setitem__(self, index, value): pass
    def __delitem__(self, index): pass

    def __getslice__(self, start, end=None):

        "Return a slice starting from 'start', with the optional 'end'."

        return _getslice(self, start, end)

    def __setslice__(self, start, end, slice): pass
    def __delslice__(self, start, end): pass

    def append(self, value):

        "Append 'value' to the list."

        native._list_append(self, value)

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

        return native._list_len(self)

    def __add__(self, other): pass

    def __iadd__(self, other):

        "Concatenate 'other' to the list."

        if isinstance(other, list):
            native._list_concat(self, other)
        else:
            self.extend(other)
        return self

    def __str__(self):

        "Return a string representation of the list."

        b = buffer()
        i = 0
        l = self.__len__()
        first = True

        # NOTE: Should really show quoted forms of the items.

        b.append("[")
        while i < l:
            if first:
                first = False
            else:
                b.append(", ")
            b.append(self.__get_single_item__(i))
        b.append("]")

        return str(b)

    def __bool__(self):

        "Lists are true if non-empty."

        return native._list_nonempty(self)

    def __iter__(self):

        "Return an iterator."

        return listiterator(self)

    # Special implementation methods.

    def __get_single_item__(self, index):

        "Return the item at the normalised (positive) 'index'."

        if index >= len(self):
            raise IndexError(index)

        return native._list_element(self, index)

# vim: tabstop=4 expandtab shiftwidth=4

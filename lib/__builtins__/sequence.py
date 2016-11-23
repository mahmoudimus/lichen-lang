#!/usr/bin/env python

"""
Sequence operations.

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

from native import _isinstance

class sequence:

    "A common base class for sequence types."

    def __getitem__(self, index):

        "Return the item or slice specified by 'index'."

        # Normalise any integer indexes, converting negative indexes to positive
        # ones.

        if _isinstance(index, int):
            index = _normalise_index(index, self.__len__())
            return self.__get_single_item__(index)

        # Handle slices separately.

        elif _isinstance(index, slice):
            return self.__getslice__(index.start, index.end)

        # No other kinds of objects are supported as indexes.

        else:
            raise TypeError

    def __getslice__(self, start, end=None):

        "Return a slice starting from 'start', with the optional 'end'."

        length = self.__len__()

        # Handle a null start as the first position, otherwise normalising any
        # start index.

        if start is None:
            start = 0
        else:
            start = _normalise_index(start, length)

        # Handle a null end as the first position after the end of the sequence,
        # otherwise normalising any end index.

        if end is None:
            end = length
        else:
            end = _normalise_index(end, length)

        result = []

        while start < end:
            result.append(self.__get_single_item__(start))
            start += 1

        return result

def _get_absolute_index(index, length):

    """
    Return the absolute index for 'index' given a collection having the
    specified 'length'.
    """

    if index < 0:
        return length + index
    else:
        return index

def _normalise_index(index, length):

    "Normalise 'index' for a collection having the specified 'length'."

    return _min(length, _max(0, _get_absolute_index(index, length)))

def _max(x, y):

    "Return the maximum of 'x' and 'y'."

    if x >= y:
        return x
    else:
        return y

def _min(x, y):

    "Return the minimum of 'x' and 'y'."

    if x <= y:
        return x
    else:
        return y

def _tuple(l): pass

# vim: tabstop=4 expandtab shiftwidth=4

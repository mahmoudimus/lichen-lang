#!/usr/bin/env python

"""
Sequence operations.

Copyright (C) 2015 Paul Boddie <paul@boddie.org.uk>

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

def _getitem(seq, index):

    "Return the item or slice specified by 'index'."

    if _isinstance(index, int):
        index = _normalise_index(index, seq.__len__())
        return seq.__get_single_item__(index)
    elif _isinstance(index, slice):
        return seq.__getslice__(index.start, index.end)
    else:
        raise TypeError

def _getslice(seq, start, end=None):

    "Return a slice starting from 'start', with the optional 'end'."

    length = seq.__len__()

    if start is None:
        start = 0
    else:
        start = _normalise_index(start, length)

    if end is None:
        end = length
    else:
        end = _normalise_index(end, length)

    result = []
    while start < end:
        result.append(seq.__get_single_item__(start))
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

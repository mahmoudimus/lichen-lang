#!/usr/bin/env python

"""
Sequence operations.

Copyright (C) 2015, 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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

from __builtins__.int import maxint
from native import isinstance as _isinstance, is_int

class itemaccess:

    "An abstract class providing item access."

    def _check_index(self, index):

        """
        Check the given absolute 'index', raising an IndexError if out of
        bounds.
        """

        if index < 0 or index >= self.__len__():
            raise IndexError(index)

    def __getitem__(self, index):

        "Return the item or slice specified by 'index'."

        # Normalise any integer indexes, converting negative indexes to positive
        # ones.

        if is_int(index):
            index = _get_absolute_index(index, self.__len__())
            return self.__get_single_item__(index)

        # Handle slices separately.

        elif _isinstance(index, slice):
            return self.__getslice__(index.start, index.end, index.step)

        # No other kinds of objects are supported as indexes.

        else:
            raise TypeError()

    def __setitem__(self, index, value):

        "Set at 'index' the given 'value'."

        # Normalise any integer indexes, converting negative indexes to positive
        # ones.

        if is_int(index):
            index = _get_absolute_index(index, self.__len__())
            return self.__set_single_item__(index, value)

        # Handle slices separately.

        elif _isinstance(index, slice):
            return self.__setslice__(index.start, index.end, value)

        # No other kinds of objects are supported as indexes.

        else:
            raise TypeError()

    def __getslice__(self, start, end=None, step=1):

        """
        Return a slice of the sequence starting from the 'start' index, ending
        before the optional 'end' (or at the end of the sequence), and providing
        items at the frequency given by 'step' (with a default step of 1).
        """

        if step == 0:
            raise ValueError(step)

        length = self.__len__()

        # Handle a null start as the first position, otherwise normalising any
        # start index.

        if start is None:
            if step > 0:
                start = 0
            else:
                start = length - 1
        else:
            start = _get_absolute_index(start, length)

        # Handle a null end as the first position after the end of the sequence,
        # otherwise normalising any end index.

        if end is None:
            if step > 0:
                end = length
            else:
                end = -1
        else:
            end = _get_absolute_index(end, length)

        return self.__get_multiple_items__(start, end, step)

    # Methods implemented by subclasses.

    def __setslice__(self, start, end, value):

        "Method to be overridden by subclasses."

        pass

    def __get_single_item__(self, index):

        "Method to be overridden by subclasses."

        return None

    def __set_single_item__(self, index, value):

        "Method to be overridden by subclasses."

        pass

    def __get_multiple_items__(self, start, end, step):

        """
        Return items from 'start' until (but excluding) 'end', at 'step'
        intervals.
        """

        result = []

        while step > 0 and start < end or step < 0 and start > end:
            result.append(self.__get_single_item__(start))
            start += step

        return result

    def __len__(self):

        "Method to be overridden by subclasses."

        return 0

class hashable(itemaccess):

    "An abstract class providing support for hashable sequences."

    _p = maxint / 32
    _a = 31

    def _hashvalue(self, fn):

        """
        Return a value for hashing purposes for the sequence using the given
        'fn' on each item.
        """

        result = 0
        l = self.__len__()
        i = 0

        while i < l:
            result = (result * self._a + fn(self.__get_single_item__(i))) % self._p
            i += 1

        return result

class sequence(itemaccess):

    "A common base class for sequence types."

    def _str(self, opening, closing):

        "Serialise this object with the given 'opening' and 'closing' strings."

        b = buffer()
        i = 0
        l = self.__len__()
        first = True

        b.append(opening)
        while i < l:
            if first:
                first = False
            else:
                b.append(", ")
            b.append(repr(self.__get_single_item__(i)))
            i += 1
        b.append(closing)

        return str(b)

    def __contains__(self, value):

        "Return whether the list contains 'value'."

        # Perform a linear search of the sequence contents.

        for v in self:

            # Return True if the current value is equal to the specified one.
            # Note that this is not an identity test, but an equality test.

            if v == value:
                return True

        return False

    def index(self, value):

        "Return the index of 'value' or raise ValueError."

        i = 0
        l = self.__len__()
        while i < l:
            if self[i] == value:
                return i
            i += 1

        raise ValueError(value)

    def __eq__(self, other):

        "Return whether this sequence is equal to 'other'."

        try:
            return self._eq(other)
        except TypeError:
            return NotImplemented

    def _eq(self, other):

        """
        Return whether this sequence is equal to 'other' sequence. Note that
        this method will raise a TypeError if 'other' is not a sequence.
        """

        # Sequences must have equal lengths to be equal.

        n = self.__len__()
        if other.__len__() != n:
            return False

        i = 0
        while i < n:
            if self.__getitem__(i) != other.__getitem__(i):
                return False
            i += 1

        return True

    def __ne__(self, other):

        "Return whether this sequence is not equal to 'other'."

        return not self.__eq__(other)

    def __iter__(self):

        "Method to be overridden by subclasses."

        raise StopIteration()

def _get_absolute_index(index, length):

    """
    Return the absolute index for 'index' given a collection having the
    specified 'length'.
    """

    if index < 0:
        return length + index
    else:
        return index

# vim: tabstop=4 expandtab shiftwidth=4

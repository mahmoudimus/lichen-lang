#!/usr/bin/env python

"""
String objects.

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

from __builtins__.operator import _negate
from __builtins__.sequence import hashable, itemaccess
from __builtins__.types import check_int
from native import str_add, str_lt, str_gt, str_eq, str_len, str_nonempty, \
                   str_substr

WHITESPACE = (" ", "\f", "\n", "\r", "\t")

class basestring(hashable):

    "The base class for all strings."

    def __init__(self, other=None):

        "Initialise the string, perhaps from 'other'."

        # Note the __data__ member. Since strings are either initialised from
        # literals or converted using routines defined for other types, no form
        # of actual initialisation is performed here.

        # NOTE: Cannot perform "other and other.__data__ or None" since the
        # NOTE: __data__ attribute is not a normal attribute.

        if other:
            self.__data__ = other.__data__
        else:
            self.__data__ = None

        # Note the __key__ member. This is also initialised statically. Where
        # a string is the same as an attribute name, the __key__ member contains
        # attribute position and code details.

        if other:
            self.__key__ = other.__key__
        else:
            self.__key__ = None

    def __hash__(self):

        "Return a value for hashing purposes."

        return self._hashvalue(ord)

    def _binary_op(self, op, other):

        "Perform 'op' on this object and 'other' if appropriate."

        # Refuse to operate on specialisations of this class.

        if self.__class__ is not other.__class__:
            return NotImplemented

        # Otherwise, perform the operation on the operands' data.

        else:
            return op(self.__data__, other.__data__)

    def _binary_op_rev(self, op, other):

        "Perform 'op' on 'other' and this object if appropriate."

        # Refuse to operate on specialisations of this class.

        if self.__class__ is not other.__class__:
            return NotImplemented

        # Otherwise, perform the operation on the operands' data.

        else:
            return op(other.__data__, self.__data__)

    def __iadd__(self, other):

        "Return a string combining this string with 'other'."

        return self._binary_op(str_add, other)

    __add__ = __iadd__

    def __radd__(self, other):

        "Return a string combining this string with 'other'."

        return self._binary_op_rev(str_add, other)

    def __mul__(self, other):

        "Multiply the string by 'other'."

        b = buffer()

        while other > 0:
            b.append(self)
            other -= 1

        return str(b)

    __rmul__ = __mul__

    def __mod__(self, other): pass
    def __rmod__(self, other): pass

    def __lt__(self, other):

        "Return whether this string is less than 'other'."

        return self._binary_op(str_lt, other)

    def __gt__(self, other):

        "Return whether this string is greater than 'other'."

        return self._binary_op(str_gt, other)

    def __le__(self, other):

        "Return whether this string is less than or equal to 'other'."

        return _negate(self.__gt__(other))

    def __ge__(self, other):

        "Return whether this string is greater than or equal to 'other'."

        return _negate(self.__lt__(other))

    def __eq__(self, other):

        "Return whether this string is equal to 'other'."

        return self._binary_op(str_eq, other)

    def __ne__(self, other):

        "Return whether this string is not equal to 'other'."

        return _negate(self.__eq__(other))

    def bytelength(self):

        "Return the number of bytes in this string."

        return str_len(self.__data__)

    __len__ = bytelength

    def __str__(self):

        "Return a string representation."

        return self

    def __repr__(self):

        "Return a program representation."

        # NOTE: To be implemented with proper quoting.
        b = buffer(['"', self, '"'])
        return str(b)

    def __bool__(self):

        "Return whether the string provides any data."

        return str_nonempty(self.__data__)

    def __contains__(self, value):

        "Return whether this string contains 'value'."

        return self.find(value) != -1

    def endswith(self, s):

        "Return whether this string ends with 's'."

        return self[-s.__len__():] == s

    def find(self, sub, start=None, end=None):

        """
        Find 'sub' in the string if it occurs from or after the 'start' position
        (or 0, if omitted) and before the 'end' position (or the end of the
        string, if omitted), returning the earliest occurrence or -1 if 'sub' is
        not present.
        """

        sublen = sub.__len__()

        i = start or 0

        if end is None:
            end = self.__len__()

        while i < end - sublen:
            if sub == self[i:i+sublen]:
                return i
            i += 1

        return -1

    def index(self, sub, start=None, end=None):

        """
        Find 'sub' in the string, starting at 'start' (or 0, if omitted), ending
        at 'end' (or the end of the string, if omitted), raising ValueError if
        'sub' is not present.
        """

        i = self.find(sub, start, end)

        if i == -1:
            raise ValueError(sub)
        else:
            return i

    def join(self, l):

        "Join the elements in 'l' with this string."

        # Empty strings just cause the list elements to be concatenated.

        if not self.__bool__():
            return str(buffer(l))

        # Non-empty strings join the elements together in a buffer.

        b = buffer()
        first = True

        for s in l:
            if first:
                first = False
            else:
                b.append(self)
            b.append(s)

        return str(b)

    def lower(self): pass
    def lstrip(self, chars=None): pass
    def replace(self, old, new, count=None): pass
    def rfind(self, sub, start=None, end=None):

        """
        Find 'sub' in the string if it occurs from or after the 'start' position
        (or 0, if omitted) and before the 'end' position (or the end of the
        string, if omitted), returning the latest occurrence or -1 if 'sub' is
        not present.
        """

        sublen = sub.__len__()

        start = start or 0

        if end is None:
            end = self.__len__()

        i = end - sublen

        while i >= start:
            if sub == self[i:i+sublen]:
                return i
            i -= 1

        return -1

    def rsplit(self, sep=None, maxsplit=None): pass
    def rstrip(self, chars=None): pass

    def split(self, sep=None, maxsplit=None):

        """
        Split the string using the given 'sep' as separator (or any whitespace
        character if omitted or specified as None), splitting at most 'maxsplit'
        times (or as many times as is possible if omitted or specified as None).
        """

        if sep is not None and not sep:
            raise ValueError, sep

        end = self.__len__()
        seplen = sep and len(sep)
        splits = 0

        l = []
        i = last = 0

        while i < end and (maxsplit is None or splits < maxsplit):

            # Find any specified separator.

            if sep and self[i:i+seplen] == sep:
                l.append(self[last:i])
                i += seplen
                last = i
                splits += 1

            # Find any whitespace character and skip adjacent characters.

            elif not sep and self[i] in WHITESPACE:
                l.append(self[last:i])
                while i < end:
                    i += 1
                    if self[i] not in WHITESPACE:
                        break
                else:
                    break
                last = i
                splits += 1

            # Check the next character.

            else:
                i += 1

        l.append(self[last:])
        return l

    def splitlines(self, keepends=False): pass

    def startswith(self, s):

        "Return whether this string starts with 's'."

        return self[:s.__len__()] == s

    def strip(self, chars=None): pass
    def upper(self): pass

class string(basestring):

    "A plain string of bytes."

    # Special implementation methods.

    def __get_single_item__(self, index):

        "Return the item at the normalised (positive) 'index'."

        self._check_index(index)
        return str_substr(self.__data__, index, index + 1, 1)

    def __get_multiple_items__(self, start, end, step):

        """
        Return items from 'start' until (but excluding) 'end', at 'step'
        intervals.
        """

        self._check_index(start)
        self._check_end_index(end)
        check_int(step)

        if step == 0:
            raise ValueError(step)

        if start == end:
            return ""

        return str_substr(self.__data__, start, end, step)

def str(obj):

    "Return the string representation of 'obj'."

    # Class attributes of instances provide __str__.

    return obj.__str__()

# vim: tabstop=4 expandtab shiftwidth=4

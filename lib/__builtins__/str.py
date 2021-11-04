#!/usr/bin/env python

"""
String objects.

Copyright (C) 2015, 2016, 2017, 2021 Paul Boddie <paul@boddie.org.uk>

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
from native import isinstance as _isinstance, \
                   str_add, str_lt, str_gt, str_eq, str_ord, \
                   str_size, str_substr

WHITESPACE = (" ", "\f", "\n", "\r", "\t")

class basestring(hashable):

    "The base class for all strings."

    def __init__(self, other=None):

        "Initialise the string, perhaps from 'other'."

        # Note the __data__ member. Since strings are either initialised from
        # literals or converted using routines defined for other types, no form
        # of actual initialisation is performed here.

        # Note the __key__ member. This is also initialised statically. Where
        # a string is the same as an attribute name, the __key__ member contains
        # attribute position and code details.

        # NOTE: Cannot perform "other and other.__data__ or None" since the
        # NOTE: __data__ attribute is not a normal attribute.

        if other:
            self.__data__ = other.__data__
            self.__key__ = other.__key__
            self.__size__ = other.__size__
        else:
            self.__data__ = None
            self.__key__ = None
            self.__size__ = None

    # Internal methods.

    def _binary_op(self, op, other, sizes=False):

        "Perform 'op' on this object and 'other' if appropriate."

        # Refuse to operate on specialisations of this class.

        if self.__class__ is not other.__class__:
            return NotImplemented

        # Otherwise, perform the operation on the operands' data.

        elif sizes:
            return op(self.__data__, other.__data__, self.__size__, other.__size__)
        else:
            return op(self.__data__, other.__data__)

    def _binary_op_rev(self, op, other, sizes=False):

        "Perform 'op' on 'other' and this object if appropriate."

        # Refuse to operate on specialisations of this class.

        if self.__class__ is not other.__class__:
            return NotImplemented

        # Otherwise, perform the operation on the operands' data.

        elif sizes:
            return op(other.__data__, self.__data__, other.__size__, self.__size__)
        else:
            return op(other.__data__, self.__data__)

    def _quote(self, quote):

        "Return a quoted representation of this string."

        b = buffer([quote])
        i = last = 0
        end = self.__len__()

        while i < end:
            c = self[i]

            # Handle quotes before anything else.

            if c == quote:
                b.append("\\")
                b.append(quote)
                i += 1
                last = i
                continue

            # Extended unquoted text.

            n = ord(c)

            if 32 <= n < 128:
                i += 1
                continue

            # Before quoting, emit unquoted text.

            b.append(self[last:i])

            # Add quoted value.

            if c == "\t":
                b.append("\\t")
            elif c == "\n":
                b.append("\\n")
            elif c == "\r":
                b.append("\\r")
            else:
                self._quote_value(b, n)

            i += 1
            last = i

        # Emit remaining unquoted text.

        b.append(self[last:])
        b.append(quote)
        return str(b)

    def _quote_value(self, b, n):

        "Append to 'b' the quoted form of 'n'."

        if n < 0:
            n += 256
        b.append("\\x")
        x = hex(n, "")
        if len(x) < 2:
            b.append("0")
        b.append(x)

    def bytelength(self):

        "Return the number of bytes in this string."

        return str_size(self.__size__)

    # General type methods.

    def __bool__(self):

        "Return whether the string provides any data."

        return str_size(self.__size__).__bool__()

    def __contains__(self, value):

        "Return whether this string contains 'value'."

        return self.find(value) != -1

    def __hash__(self):

        "Return a value for hashing purposes."

        return self._hashvalue(ord)

    __len__ = bytelength

    def __repr__(self):

        "Return a program representation."

        return self._quote('"')

    def __str__(self):

        "Return a string representation."

        return self

    # Operator methods.

    def __iadd__(self, other):

        "Return a string combining this string with 'other'."

        return self._binary_op(str_add, other, True)

    __add__ = __iadd__

    def __radd__(self, other):

        "Return a string combining this string with 'other'."

        return self._binary_op_rev(str_add, other, True)

    def __mod__(self, other):

        "Format 'other' using this string."

        if not _isinstance(other, tuple):
            other = [other]

        i = 0
        first = True
        b = buffer()

        for s in self.split("%"):
            if first:
                b.append(s)
                first = False
                continue

            # Handle format codes.
            # NOTE: To be completed.

            if s.startswith("%"):
                b.append(s)

            elif s.startswith("s"):
                b.append(str(other[i]))
                b.append(s[1:])
                i += 1

            elif s.startswith("r"):
                b.append(repr(other[i]))
                b.append(s[1:])
                i += 1

            # Unrecognised code: probably just a stray %.

            else:
                b.append("%")
                b.append(s)

        return str(b)

    def __rmod__(self, other): pass

    def __mul__(self, other):

        "Multiply the string by 'other'."

        b = buffer()

        while other > 0:
            b.append(self)
            other -= 1

        return str(b)

    __rmul__ = __mul__

    # Comparison methods.

    def __eq__(self, other):

        "Return whether this string is equal to 'other'."

        return self._binary_op(str_eq, other)

    def __ge__(self, other):

        "Return whether this string is greater than or equal to 'other'."

        return _negate(self.__lt__(other))

    def __gt__(self, other):

        "Return whether this string is greater than 'other'."

        return self._binary_op(str_gt, other)

    def __le__(self, other):

        "Return whether this string is less than or equal to 'other'."

        return _negate(self.__gt__(other))

    def __lt__(self, other):

        "Return whether this string is less than 'other'."

        return self._binary_op(str_lt, other)

    def __ne__(self, other):

        "Return whether this string is not equal to 'other'."

        return _negate(self.__eq__(other))

    # String-specific methods.

    def __ord__(self):

        "Return the value of the string, if only a single character."

        if self.__len__() == 1:
            return str_ord(self.__data__)
        else:
            raise ValueError, self

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

        if end is None:
            end = self.__len__()

        end -= sublen

        i = start or 0

        while i <= end:
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

    def lstrip(self, chars=None):

        """
        Strip any of the given 'chars' from the start of the string, or strip
        whitespace characters is 'chars' is omitted or None.
        """

        if chars is not None and not chars:
            return self

        i = 0
        end = self.__len__()

        while i < end and self[i] in (chars or WHITESPACE):
            i += 1

        return self[i:]

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

    def rsplit(self, sep=None, maxsplit=None):

        """
        Split the string using the given 'sep' as separator (or any whitespace
        character if omitted or specified as None), splitting at most 'maxsplit'
        times (or as many times as is possible if omitted or specified as None).
        Where 'maxsplit' is given, the number of split points is counted from
        the end of the string.
        """

        if not maxsplit:
            return self.split(sep, maxsplit)

        if sep is not None and not sep:
            raise ValueError, sep

        seplen = sep and len(sep) or 1
        start = seplen
        splits = 0

        l = []
        i = last = self.__len__()

        while i >= start and (maxsplit is None or splits < maxsplit):

            # Find any specified separator.

            if sep and self[i-seplen:i] == sep:
                l.insert(0, self[i:last])
                i -= seplen
                last = i
                splits += 1

            # Find any whitespace character and skip adjacent characters.

            elif not sep and self[i-1] in WHITESPACE:
                l.insert(0, self[i:last])
                while i > start:
                    i -= 1
                    if self[i-1] not in WHITESPACE:
                        break
                else:
                    break
                last = i
                splits += 1

            # Check the next character.

            else:
                i -= 1

        l.insert(0, self[:last])
        return l

    def rstrip(self, chars=None):

        """
        Strip any of the given 'chars' from the end of the string, or strip
        whitespace characters is 'chars' is omitted or None.
        """

        if chars is not None and not chars:
            return self

        i = self.__len__() - 1

        while i >= 0 and self[i] in (chars or WHITESPACE):
            i -= 1

        return self[:i+1]

    def split(self, sep=None, maxsplit=None):

        """
        Split the string using the given 'sep' as separator (or any whitespace
        character if omitted or specified as None), splitting at most 'maxsplit'
        times (or as many times as is possible if omitted or specified as None).
        Where 'maxsplit' is given, the number of split points is counted from
        the start of the string.
        """

        if sep is not None and not sep:
            raise ValueError, sep

        if maxsplit is not None and not maxsplit:
            return [self]

        seplen = sep and len(sep) or 1
        end = self.__len__() - seplen
        splits = 0

        l = []
        i = last = 0

        while i <= end and (maxsplit is None or splits < maxsplit):

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

    def strip(self, chars=None):

        """
        Strip any of the given 'chars' from the start and end of the string, or
        strip whitespace characters is 'chars' is omitted or None.
        """

        return self.lstrip(chars).rstrip(chars)

    def upper(self): pass

class str(basestring):

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

        if start == end:
            return ""

        check_int(step)

        if step == 0:
            raise ValueError(step)

        l = get_using(basestring.__get_multiple_items__, self)(start, end, step)
        return "".join(l)

def new_str(obj):

    "Return the string representation of 'obj'."

    # Class attributes of instances provide __str__.

    return obj.__str__()

# vim: tabstop=4 expandtab shiftwidth=4

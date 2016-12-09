#!/usr/bin/env python

"""
String objects.

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

from __builtins__.int import maxint, minint
from __builtins__.operator import _negate
from __builtins__.sequence import itemaccess
from native import str_add, str_lt, str_gt, str_eq, str_len, str_nonempty, \
                   str_substr

class basestring(itemaccess):

    "The base class for all strings."

    _p = maxint / 32
    _a = 31

    def __init__(self):

        "Initialise the string."

        # Note the __data__ member. Since strings are either initialised from
        # literals or converted using routines defined for other types, no form
        # of actual initialisation is performed here.

        self.__data__ = None

        # Note the __key__ member. This is also initialised statically. Where
        # a string is the same as an attribute name, the __key__ member contains
        # attribute position and code details.

        self.__key__ = None

    def __hash__(self):

        "Return a value for hashing purposes."

        result = 0
        l = self.__len__()
        i = 0

        while i < l:
            result = (result * self._a + ord(self.__get_single_item__(i))) % self._p
            i += 1

        return result

    def _binary_op(self, op, other):

        "Perform 'op' on this int and 'other' if appropriate."

        if isinstance(other, basestring):
            return op(self.__data__, other.__data__)
        else:
            return NotImplemented

    def __iadd__(self, other):

        "Return a string combining this string with 'other'."

        return self._binary_op(str_add, other)

    __add__ = __radd__ = __iadd__

    def __mul__(self, other): pass
    def __rmul__(self, other): pass
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

    def __len__(self):

        "Return the length of this string."

        return str_len(self.__data__)

    def __str__(self):

        "Return a string representation."

        return self

    def __repr__(self):

        "Return a program representation."

        # NOTE: To be implemented with proper quoting.
        b = buffer(['"', self, '"'])
        return str(b)

    def __bool__(self):
        return str_nonempty(self.__data__)

    def endswith(self, s): pass
    def find(self, sub, start=None, end=None): pass
    def index(self, sub, start=None, end=None): pass

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
    def rfind(self, sub, start=None, end=None): pass
    def rsplit(self, sep=None, maxsplit=None): pass
    def rstrip(self, chars=None): pass
    def split(self, sep=None, maxsplit=None): pass
    def splitlines(self, keepends=False): pass
    def startswith(self, s): pass
    def strip(self, chars=None): pass
    def upper(self): pass

    # Special implementation methods.

    def __get_single_item__(self, index):

        "Return the item at the normalised (positive) 'index'."

        self._check_index(index)
        return str_substr(self.__data__, index, 1)

class string(basestring):
    pass

class unicode(basestring):
    def encode(self, encoding): pass

def str(obj):

    "Return the string representation of 'obj'."

    # Class attributes of instances provide __str__.

    return obj.__str__()

# vim: tabstop=4 expandtab shiftwidth=4

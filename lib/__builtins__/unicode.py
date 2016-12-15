#!/usr/bin/env python

"""
Unicode objects.

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

from __builtins__.str import basestring
from posix.iconv import Converter
from native import str_add, unicode_len, isinstance as _isinstance

class utf8string(basestring):

    "A character string representation based on UTF-8."

    def __init__(self, other=None, encoding=None):

        """
        Initialise the string, perhaps from 'other', with any original
        'encoding' indicated.
        """

        get_using(basestring.__init__, self)(other)
        self.encoding = encoding
        self.length = None

    def _binary_op(self, op, other):

        "Perform 'op' on this object and 'other' if appropriate."

        # Reject non-strings.

        if not _isinstance(other, basestring):
            return NotImplemented

        # Combining text with bytes.

        elif not _isinstance(other, utf8string):
            s = self.encode()
            return op(s.__data__, other.__data__)

        # Otherwise, perform the operation on the operands' data.

        else:
            return op(self.__data__, other.__data__)

    def _binary_op_rev(self, op, other):

        "Perform 'op' on 'other' and this object if appropriate."

        # Reject non-strings.

        if not _isinstance(other, basestring):
            return NotImplemented

        # Combining text with bytes.

        elif not _isinstance(other, utf8string):
            s = self.encode()
            return op(other.__data__, s.__data__)

        # Otherwise, perform the operation on the operands' data.

        else:
            return op(other.__data__, self.__data__)

    def _convert(self, result, other):

        "Convert 'result' to a Unicode object if 'other' already is."

        if _isinstance(other, utf8string):
            return utf8string(result, self.encoding)
        else:
            return result

    def __iadd__(self, other):

        "Return a string combining this string with 'other'."

        return self._convert(self._binary_op(str_add, other), other)

    __add__ = __iadd__

    def __radd__(self, other):

        "Return a string combining this string with 'other'."

        return self._convert(self._binary_op_rev(str_add, other), other)

    def __len__(self):

        "Return the length of this string in characters."

        if self.length is None:
            self.length = unicode_len(self.__data__)

        return self.length

    def encode(self, encoding=None):

        """
        Encode the string to the given 'encoding' or any original encoding if
        omitted.
        """

        encoding = encoding or self.encoding
        if not encoding:
            return self

        from_utf8 = Converter("UTF-8", encoding)

        try:
            from_utf8.feed(self)
            return str(from_utf8)

        finally:
            from_utf8.close()

    def join(self, l):

        "Join the elements in 'l' with this string."

        # Empty strings just cause the list elements to be concatenated.

        nonempty = self.__bool__()

        # Non-empty strings join the elements together in a buffer.

        b = buffer()
        first = True
        encoding = self.encoding

        for s in l:
            if first:
                first = False
            elif nonempty:
                b.append(self)

            if _isinstance(s, utf8string):
                encoding = None

            b.append(s)

        s = str(b)
        if encoding:
            s = utf8string(s)
            s.encoding = encoding
        return s

def unicode(s, encoding):

    "Convert 's' to a Unicode object, interpreting 's' as using 'encoding'."

    if isinstance(s, utf8string):
        return s

    # Obtain a string representation.

    s = s.__str__()

    # Convert the string to UTF-8.

    to_utf8 = Converter(encoding, "UTF-8")

    try:
        to_utf8.feed(s)
        return utf8string(str(to_utf8), encoding)

    finally:
        to_utf8.close()

# vim: tabstop=4 expandtab shiftwidth=4

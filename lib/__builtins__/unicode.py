#!/usr/bin/env python

"""
Unicode objects.

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

from __builtins__.str import basestring
from __builtins__.types import check_int
from posix.iconv import Converter
from native import str_add, unicode_len, unicode_ord, unicode_substr, \
                   isinstance as _isinstance

class unicode(basestring):

    "A character string representation based on UTF-8."

    def __init__(self, s, encoding=None, original=None):

        """
        Initialise the string from 'other', employing any indicated 'encoding'
        for the provided string data.

        If 'original' is indicated, this may be used to override the original
        encoding. This is useful when the string data is already in UTF-8
        format, but where the original encoding needs to be communicated.
        """

        self.length = None

        # Initialise using another Unicode object.

        if _isinstance(s, unicode):
            get_using(basestring.__init__, self)(s)
            self.encoding = s.encoding

        # Initialise using suitable string data but with an explicit original
        # encoding.

        elif original:
            get_using(basestring.__init__, self)(s)
            self.encoding = original

        # Initialise using string data having either UTF-8 or another encoding,
        # converting to UTF-8 and retaining the encoding details as the original
        # encoding.

        else:
            # Obtain a string representation.

            s = s.__str__()

            # Convert the string to UTF-8. Even if the stated encoding is UTF-8, it
            # needs to be validated.

            to_utf8 = Converter(encoding or "UTF-8", "UTF-8")

            try:
                to_utf8.feed(s)
                get_using(basestring.__init__, self)(str(to_utf8))
            finally:
                to_utf8.close()

            self.encoding = encoding

    def _binary_op(self, op, other, sizes=False):

        "Perform 'op' on this object and 'other' if appropriate."

        # Reject non-strings.

        if not _isinstance(other, basestring):
            return NotImplemented

        # Combining text with bytes.

        if not _isinstance(other, unicode):
            s = self.encode()
        else:
            s = self

        if sizes:
            return op(s.__data__, other.__data__, s.__size__, other.__size__)
        else:
            return op(s.__data__, other.__data__)

    def _binary_op_rev(self, op, other, sizes=False):

        "Perform 'op' on 'other' and this object if appropriate."

        # Reject non-strings.

        if not _isinstance(other, basestring):
            return NotImplemented

        # Combining text with bytes.

        if not _isinstance(other, unicode):
            s = self.encode()
        else:
            s = self

        if sizes:
            return op(other.__data__, s.__data__, other.__size__, s.__size__)
        else:
            return op(other.__data__, s.__data__)

    def _convert(self, result, other):

        "Convert 'result' to a Unicode object if 'other' already is."

        if _isinstance(other, unicode):
            return unicode(result, None, self.encoding)
        else:
            return result

    def _quote_value(self, b, n):

        "Append to 'b' the quoted form of 'n'."

        if n < 0:
            n += 256

        if n > 0xffff:
            b.append("\\U")
            digits = 8
        else:
            b.append("\\u")
            digits = 4

        x = hex(n, "")
        i = len(x)

        while i < digits:
            b.append("0")
            i += 1

        b.append(x)

    # Operator methods.

    def __iadd__(self, other):

        "Return a string combining this string with 'other'."

        return self._convert(self._binary_op(str_add, other, True), other)

    __add__ = __iadd__

    def __radd__(self, other):

        "Return a string combining this string with 'other'."

        return self._convert(self._binary_op_rev(str_add, other, True), other)

    def __len__(self):

        "Return the length of this string in characters."

        if self.length is None:
            self.length = unicode_len(self.__data__, self.__size__)

        return self.length

    def __ord__(self):

        "Return the value of the string, if only a single character."

        if self.__len__() == 1:
            return unicode_ord(self.__data__, self.__size__)
        else:
            raise ValueError, self

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

            if _isinstance(s, unicode):
                encoding = None

            b.append(s)

        s = str(b)
        if encoding:
            s = unicode(s, None, encoding)
        return s

    # Special implementation methods.

    def __get_single_item__(self, index):
    
        "Return the item at the normalised (positive) 'index'."
 
        self._check_index(index)
        return unicode(unicode_substr(self.__data__, self.__size__, index, index + 1, 1), None, self.encoding)

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
        return unicode("".join(l), None, self.encoding)

# vim: tabstop=4 expandtab shiftwidth=4

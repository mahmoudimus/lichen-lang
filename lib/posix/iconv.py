#!/usr/bin/env python

"""
POSIX character set conversion functions.

Copyright (C) 2016 Paul Boddie <paul@boddie.org.uk>

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

from __builtins__.types import check_int, check_string
from native import iconv_close, iconv_open, iconv

class ConverterError(Exception):

    "An error indicating a failure involving a character set converter."

    pass

E2BIG = 7
EINVAL = 22
EILSEQ = 84

class Converter:

    "A character set converter."

    def __init__(self, from_encoding, to_encoding):

        "Initialise conversion between 'from_encoding' and 'to_encoding'."

        check_string(from_encoding)
        check_string(to_encoding)
        self.__data__ = iconv_open(to_encoding, from_encoding)

    def close(self):

        "Close this converter."

        iconv_close(self.__data__)
        self.__data__ = None

    def convert(self, s):

        "Convert 's' between the converter's encodings."

        if self.__data__ is None:
            raise ConverterError

        check_string(s)

        result = []
        state = [0, len(s)]

        while True:

            # Obtain converted text and update the state.

            out = iconv(self.__data__, s, state)
            result.append(out)

            # Test for the end of the conversion.

            start, remaining = state
            if not remaining:
                return "".join(result)

# vim: tabstop=4 expandtab shiftwidth=4

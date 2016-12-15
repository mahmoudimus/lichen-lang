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
from native import iconv, iconv_close, iconv_open, iconv_reset

# Errors produced by iconv.

EINVAL = 22
EILSEQ = 84

class ConverterError(Exception):

    "An error indicating a failure involving a character set converter."

    pass

class Converter:

    "A character set converter."

    def __init__(self, from_encoding, to_encoding):

        "Initialise conversion between 'from_encoding' and 'to_encoding'."

        check_string(from_encoding)
        check_string(to_encoding)
        self.__data__ = iconv_open(to_encoding, from_encoding)
        self.reset()

    def reset(self):

        "Reset the state of the converter."

        self.state = ["", 0, 0]
        self.result = []
        iconv_reset(self.__data__)

    def close(self):

        "Close this converter."

        iconv_close(self.__data__)
        self.__data__ = None

    def feed(self, s):

        "Feed 's' to the converter, converting its byte representation."

        if self.__data__ is None:
            raise ConverterError

        check_string(s)

        _s, start, remaining = self.state

        if _s:
            self.state = [_s + s, start, remaining + s.bytelength()]
        else:
            self.state = [s, 0, s.bytelength()]

        while True:

            # Obtain converted text and update the state.

            try:
                out = iconv(self.__data__, self.state)

            # Incomplete input does not cause an exception.

            except OSError, exc:
                if exc.value == EINVAL:
                    self.result.append(exc.arg)
                    return
                elif exc.value == EILSEQ:
                    raise UnicodeDecodeError(exc.arg)
                else:
                    raise

            # Add any returned text to the result.

            self.result.append(out)

            # Test for the end of the conversion.

            _s, start, remaining = self.state

            if not remaining:
                return

    def __str__(self):

        "Return the value of the converted string."

        return "".join(self.result)

# vim: tabstop=4 expandtab shiftwidth=4

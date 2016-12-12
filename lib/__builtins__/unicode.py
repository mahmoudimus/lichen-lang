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

class utf8string(basestring):

    "A character string representation based on UTF-8."

    def encode(self, encoding):

        "Encode the string to the given 'encoding'."

        from_utf8 = Converter("UTF-8", encoding)
        try:
            from_utf8.feed(self)
            return str(from_utf8)
        finally:
            from_utf8.close()

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
        return utf8string(str(to_utf8))
    finally:
        to_utf8.close()

# vim: tabstop=4 expandtab shiftwidth=4

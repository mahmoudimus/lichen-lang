#!/usr/bin/env python

"""
File objects.

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

from __builtins__.types import check_int, check_string
from native import isinstance as _isinstance, fclose, fopen, fread, fwrite

class filestream:

    "Generic file-oriented stream functionality."

    def __init__(self, encoding=None, bufsize=1024):

        "Initialise the stream with the given 'encoding' and 'bufsize'."

        self.encoding = encoding
        self.bufsize = bufsize
        self.__data__ = None

    def read(self, n=0):

        "Read 'n' bytes from the stream."

        check_int(n)

        # Read any indicated number of bytes.

        if n > 0:
            s = fread(self.__data__, n)

        # Read all remaining bytes.

        else:
            l = []

            # Read until end-of-file.

            try:
                while True:
                    l.append(fread(self.__data__, self.bufsize))

            # Handle end-of-file reads.

            except EOFError:
                pass

            s = "".join(l)

        # Convert bytes to text if necessary.

        if self.encoding:
            return unicode(s, self.encoding)
        else:
            return s

    def write(self, s):

        "Write string 's' to the stream."

        check_string(s)

        # Encode text as bytes if necessary.

        if self.encoding and _isinstance(s, utf8string):
            s = s.encode(self.encoding)

        fwrite(self.__data__, s)

    def close(self):

        "Close the stream."

        fclose(self.__data__)

class file(filestream):

    "A file abstraction."

    def __init__(self, filename, mode="r", encoding=None, bufsize=1024):

        """
        Open the file with the given 'filename' using the given access 'mode',
        any specified 'encoding', and the given 'bufsize'.
        """

        get_using(filestream.__init__, self)(encoding, bufsize)
        self.__data__ = fopen(filename, mode)

    def readline(self, size=None): pass
    def readlines(self, size=None): pass

# vim: tabstop=4 expandtab shiftwidth=4

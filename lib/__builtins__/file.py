#!/usr/bin/env python

"""
File objects.

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

from __builtins__.stream import filestream
from native import fopen, fread

class file(filestream):

    "A file abstraction."

    def __init__(self, filename, mode="r", encoding=None, bufsize=1024):

        """
        Open the file with the given 'filename' using the given access 'mode',
        any specified 'encoding', and the given 'bufsize'.
        """

        get_using(filestream.__init__, self)(encoding, bufsize)
        self.__data__ = fopen(filename, mode)
        self.buffered = ""

    def _get_data(self):

        "Get data from the file."

        if self.buffered:
            s = self.buffered
            self.buffered = ""
        else:
            s = fread(self.__data__, self.bufsize)

        return s

    def _read_data(self, l):

        "Read data into 'l'."

        s = self._get_data()
        l.append(s)

    def _read_until_newline(self, l):

        "Read data into 'l', returning whether a newline has been read."

        s = self._get_data()

        # NOTE: Only POSIX newlines are supported currently.

        i = s.find("\n")

        if i != -1:
            l.append(s[:i+1])
            self.buffered = s[i+1:]
            return True

        l.append(s)
        return False

# vim: tabstop=4 expandtab shiftwidth=4

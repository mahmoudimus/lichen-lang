#!/usr/bin/env python

"""
C library input/output.

Copyright (C) 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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
from __builtins__.types import check_int, check_string

import locale

from native import (
    close as _close,
    fdopen as _fdopen,
    read as _read,
    write as _write
    )

# Abstractions for system-level files and streams.

class sysfile:

    "A system-level file object."

    def __init__(self, fd):

        "Initialise the file with the given 'fd'."

        self.fd = fd

    def read(self, n):

        "Read 'n' bytes from the file, returning a string."

        return read(self.fd, n)

    def write(self, s):

        "Write string 's' to the file."

        return write(self.fd, s)

    def close(self):

        "Close the file."

        close(self.fd)

class sysstream(filestream):

    "A system-level stream object."

    def __init__(self, fd, mode="r", encoding=None, bufsize=1024):

        """
        Initialise the stream with the given 'fd', 'mode', 'encoding' and
        'bufsize'.
        """

        check_int(fd)
        check_string(mode)

        get_using(filestream.__init__, self)(encoding, bufsize)
        self.__data__ = _fdopen(fd, mode)

# Standard streams.

stdin = sysstream(0)
stdout = sysstream(1, "w")
stderr = sysstream(2, "w")

# Localised streams.
# Perform locale initialisation explicitly to ensure that the locale module
# and various function defaults have been initialised.

locale.initlocale()
lstdin = sysstream(0, "r", locale.getpreferredencoding())

# Input/output functions.

def close(fd):

    "Close the file descriptor 'fd'."

    _close(fd)

def fdopen(fd, mode="r"):

    """
    Open a stream for the given file descriptor 'fd', operating in the given
    'mode'.
    """

    return sysstream(fd, mode)

def read(fd, n):

    """
    Read using the low-level file descriptor 'fd' the given number of bytes 'n'.
    """

    check_int(fd)
    check_int(n)
    return _read(fd, n)

def write(fd, s):

    "Write using the low-level file descriptor 'fd' the given string 's'."

    check_int(fd)
    check_string(s)
    return _write(fd, s)

# vim: tabstop=4 expandtab shiftwidth=4

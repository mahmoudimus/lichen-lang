#!/usr/bin/env python

"""
POSIX input/output functions.

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

from libc.io import close, fdopen, read, write

def closerange(fd_low, fd_high): pass
def dup(fd): pass
def dup2(old_fd, new_fd): pass
def fchdir(fd): pass
def fchmod(fd, mode): pass
def fchown(fd, uid, gid): pass
def fdatasync(fd): pass
def fpathconf(fd, name): pass
def fstat(fd): pass
def fstatvfs(fd): pass
def fsync(fd): pass
def ftruncate(fd, length): pass
def isatty(fd): pass

SEEK_CUR = 1
SEEK_END = 2
SEEK_SET = 0

def lseek(fd, pos, how): pass
def open(filename, flag, mode=0777): pass
def openpty(): pass
def pipe(): pass
def putenv(key, value): pass
def times(): pass
def ttyname(fd): pass
def umask(new_mask): pass
def uname(): pass
def unsetenv(key): pass

# Constants.

O_APPEND = 1024
O_ASYNC = 8192
O_CREAT = 64
O_DIRECT = 16384
O_DIRECTORY = 65536
O_DSYNC = 4096
O_EXCL = 128
O_LARGEFILE = 32768
O_NDELAY = 2048
O_NOATIME = 262144
O_NOCTTY = 256
O_NOFOLLOW = 131072
O_NONBLOCK = 2048
O_RDONLY = 0
O_RDWR = 2
O_RSYNC = 1052672
O_SYNC = 1052672
O_TRUNC = 512
O_WRONLY = 1

# vim: tabstop=4 expandtab shiftwidth=4

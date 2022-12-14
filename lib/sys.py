#!/usr/bin/env python

"""
System functions and objects.

Copyright (C) 2008, 2012, 2014, 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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
from libc.io import lstdin, stdin, stdout, stderr

from native import (
    exit as _exit,
    get_argv as _get_argv,
    get_path as _get_path
    )

# NOTE: Environment details to be implemented.

argv = _get_argv()
path = _get_path()

# Functions to be implemented natively.

def exit(status=0):
    _exit(int(status))

# vim: tabstop=4 expandtab shiftwidth=4

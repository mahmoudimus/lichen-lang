#!/usr/bin/env python

"""
System functions and objects.

Copyright (C) 2008, 2012, 2014, 2016 Paul Boddie <paul@boddie.org.uk>

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

from native import _exit

# Placeholders for run-time data.

stdin = file()
stdout = file()
stderr = file()

argv = []
path = []

hexversion = 0x20703f0  # 2.7.3 final 0
maxint = 2147483647     # 2**31 - 1
maxunicode = 1114111
platform = 'posix'

# Functions to be implemented natively.

def exit(status=0):
    _exit(int(status))

# vim: tabstop=4 expandtab shiftwidth=4

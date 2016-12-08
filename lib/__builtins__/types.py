#!/usr/bin/env python

"""
Common type validation functions.

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

import native

def check_int(i):

    "Check the given int 'i'."

    if not native._isinstance(i, int):
        raise ValueError(i)

def check_string(s):

    "Check the given string 's'."

    if not native._isinstance(s, string):
        raise ValueError(s)

# vim: tabstop=4 expandtab shiftwidth=4

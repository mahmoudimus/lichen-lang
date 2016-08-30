#!/usr/bin/env python

"""
Operator support.

Copyright (C) 2010, 2013, 2015 Paul Boddie <paul@boddie.org.uk>

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

# Necessary import since the operator module gets imported very early during
# builtins initialisation.

from __builtins__.span import slice

# NOTE: The compiler should make it possible for the following functions to call
# NOTE: the generic operator implementations with no additional call overhead.

# Access and slicing functions.

def getitem(a, b):
    return a.__getitem__(b)

def setitem(a, b, c):
    a.__setitem__(b, c)

# NOTE: Should be able to optimise temporary instance allocations for slices.

def getslice(a, b, c):
    return a.__getitem__(slice(b, c))

def setslice(a, b, c, d):
    a.__setitem__(slice(b, c), d)

# vim: tabstop=4 expandtab shiftwidth=4

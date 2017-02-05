#!/usr/bin/env python

"""
Operator support.

Copyright (C) 2010, 2013, 2015, 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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

# Access and slicing functions.

def delitem(a, b):
    a.__delitem__(b)

def getitem(a, b):
    return a.__getitem__(b)

def setitem(a, b, c):
    a.__setitem__(b, c)

def delslice(a, b, c):
    a.__delitem__(slice(b, c))

def getslice(a, b, c):
    return a.__getitem__(slice(b, c))

def setslice(a, b, c, d):
    a.__setitem__(slice(b, c), d)

# vim: tabstop=4 expandtab shiftwidth=4

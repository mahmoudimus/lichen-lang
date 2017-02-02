#!/usr/bin/env python

"""
Enumeration-related functions.

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

def enumerate(iterable, start=0):

    """
    Iterate over 'iterable', obtaining items and combining them with position
    information, producing a sequence containing tuples of the form
    (position, item). The first position is indicated by 'start' (which is zero
    by default) and each subsequent positions is incremented from the one
    preceding it.
    """

    l = []
    pos = start

    for i in iterable:
        l.append((pos, i))
        pos += 1

    return l

# vim: tabstop=4 expandtab shiftwidth=4

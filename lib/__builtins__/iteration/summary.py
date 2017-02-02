#!/usr/bin/env python

"""
Iterator summary functions.

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

def max(args):

    "Implementation of max."

    highest = None
    for arg in args:
        if highest is None or arg > highest:
            highest = arg
    return highest

def min(args):

    "Implementation of min."

    lowest = None
    for arg in args:
        if lowest is None or arg < lowest:
            lowest = arg
    return lowest

def sum(sequence, start=0):

    "Sum the elements in 'sequence', adding to any indicated 'start' value."

    total = start
    for i in sequence:
        total += i
    return total

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"""
Iteration-related functions.

Copyright (C) 2015 Paul Boddie <paul@boddie.org.uk>

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

from __builtins__.span import xrange

def all(iterable): pass
def any(iterable): pass
def enumerate(iterable): pass
def filter(function, sequence): pass
def iter(collection):

    "Implementation of iter without callable plus sentinel support."

    return collection.__iter__()

def len(obj):

    "Implementation of len."

    return obj.__len__()

def map(function, *args): pass

def max(*args):

    "Implementation of max."

    highest = args[0]
    for arg in args[1:]:
        if arg > highest:
            highest = arg
    return highest

def min(*args):

    "Implementation of min."

    lowest = args[0]
    for arg in args[1:]:
        if arg > lowest:
            lowest = arg
    return lowest

def range(start_or_end, end=None, step=1):

    "Implementation of range."

    return list(xrange(start_or_end, end, step))

def reduce(function, sequence, initial=None): pass
def reversed(sequence): pass
def sorted(iterable, cmp=None, key=None, reverse=False): pass
def sum(sequence, start=0): pass
def zip(*args): pass

# vim: tabstop=4 expandtab shiftwidth=4

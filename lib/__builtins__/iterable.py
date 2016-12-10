#!/usr/bin/env python

"""
Iteration-related functions.

Copyright (C) 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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

def all(iterable): pass
def any(iterable): pass

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

def filter(function, sequence):

    """
    Apply 'function' to each element in 'sequence', returning a sequence of all
    elements for which the result of the function evaluated to a true value.
    """

    l = []
    for i in sequence:
        if function(i):
            l.append(i)
    return l

def iter(collection):

    "Implementation of iter without callable plus sentinel support."

    return collection.__iter__()

def len(obj):

    "Implementation of len."

    return obj.__len__()

def map(function, sequence):

    """
    Apply 'function' to each element of 'sequence' in turn, appending the result
    to a new sequence containing all results.
    """

    l = []
    for i in sequence:
        l.append(function(i))
    return l

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

_reduce_default = object()

def reduce(function, sequence, initial=_reduce_default):

    """
    Using 'function', reduce the given 'sequence' to a single result.

    With no 'initial' value specified, the first two elements in the 'sequence'
    are used with the function to produce an initial result. With an initial
    result available, a subsequent result is computed by using the initial
    result and the next element in the sequence with the function.

    All subsequent results are computed using the current result and the next
    available element with the function. This continues for all remaining
    elements until the end of the sequence is reached.
    """

    result = initial

    for i in sequence:
        if result is _reduce_default:
            result = i
        else:
            result = function(result, i)

    return result

def reversed(sequence):

    "Return a reversed version of the given 'sequence'."

    return sequence[::-1]

def sorted(iterable, cmp=None, key=None, reverse=False): pass

def sum(sequence, start=0):

    "Sum the elements in 'sequence', adding to any indicated 'start' value."

    total = start
    for i in sequence:
        total += i
    return total

def zip(args):

    """
    Zip the given 'args' together, producing for each index position tuples
    containing the values for that position from each of the 'args'.
    """

    result = []
    pos = 0

    # Repeat until one of the arguments runs out of elements.

    while True:
        l = []

        # Visit each argument in turn, collecting elements in the given
        # position.

        for arg in args:
            try:
                l.append(arg[pos])
            except IndexError:
                return result

        result.append(tuple(l))
        pos += 1

# vim: tabstop=4 expandtab shiftwidth=4

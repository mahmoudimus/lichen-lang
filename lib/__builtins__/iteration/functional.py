#!/usr/bin/env python

"""
Functional operations for iterators.

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

def map(function, sequence):

    """
    Apply 'function' to each element of 'sequence' in turn, appending the result
    to a new sequence containing all results.
    """

    l = []
    for i in sequence:
        l.append(function(i))
    return l

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

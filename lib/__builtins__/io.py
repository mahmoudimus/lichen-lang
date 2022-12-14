#!/usr/bin/env python

"""
Input/output-related functions.

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

from sys import lstdin, stdout

open = file

def raw_input(prompt=None):

    """
    Write any specified 'prompt' to standard output and read text from standard
    input.
    """

    if prompt:
        stdout.write(prompt)
        stdout.flush()

    return lstdin.readline()

def print_(dest, args, nl):

    """
    Write to 'dest' the string representation of 'args', adding a newline if
    'nl' is given as a true value.
    """

    # Write to standard output if dest is not specified.

    dest = dest or stdout

    first = True

    for arg in args:

        # Insert spaces between arguments.

        if first:
            first = False
        else:
            dest.write(" ")

        dest.write(str(arg))

    # Add a newline if specified.

    if nl:
        dest.write("\n")
    else:
        dest.write(" ")

# vim: tabstop=4 expandtab shiftwidth=4

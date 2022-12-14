#!/usr/bin/env python

"""
Operator-related functions.

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

def _binary_op(this, other, op):

    "Test the types of 'this' and 'other', performing 'op' if identical."

    if this.__class__ is other.__class__:
        return op(this, other)
    else:
        return NotImplemented

def _negate(result):

    "Negate any valid logical value."

    if result is NotImplemented:
        return result
    else:
        return not result

# vim: tabstop=4 expandtab shiftwidth=4

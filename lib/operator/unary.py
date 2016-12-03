#!/usr/bin/env python

"""
Operator support.

Copyright (C) 2010, 2013, 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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

from operator.core import unary_op

# These functions defer method lookup by wrapping the attribute access in
# lambda functions. Thus, the appropriate methods are defined locally, but no
# attempt to obtain them is made until the generic function is called.

# Unary operator functions.

def invert(a):
    return unary_op(a, lambda a: a.__invert__)

def neg(a):
    return unary_op(a, lambda a: a.__neg__)

def not_(a):
    return not a

def pos(a):
    return unary_op(a, lambda a: a.__pos__)

# vim: tabstop=4 expandtab shiftwidth=4

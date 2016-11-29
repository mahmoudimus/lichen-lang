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

from operator.core import binary_op

# These functions defer method lookup by wrapping the attribute access in
# lambda functions. Thus, the appropriate methods are defined locally, but no
# attempt to obtain them is made until the generic function is called.

# Comparison functions.

def eq(a, b):
    return binary_op(a, b, lambda a: a.__eq__, lambda b: b.__eq__, False)

def ge(a, b):
    return binary_op(a, b, lambda a: a.__ge__, lambda b: b.__le__)

def gt(a, b):
    return binary_op(a, b, lambda a: a.__gt__, lambda b: b.__lt__)

def le(a, b):
    return binary_op(a, b, lambda a: a.__le__, lambda b: b.__ge__)

def lt(a, b):
    return binary_op(a, b, lambda a: a.__lt__, lambda b: b.__gt__)

def ne(a, b):
    return binary_op(a, b, lambda a: a.__ne__, lambda b: b.__ne__, True)

# vim: tabstop=4 expandtab shiftwidth=4

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

from operator.core import binary_op, is_, is_not
from native import int_add, int_div, int_mod, int_mul, int_pow, int_sub, \
                   int_and, int_not, int_or, int_xor, \
                   is_int

# These functions defer method lookup by wrapping the attribute access in
# lambda functions. Thus, the appropriate methods are defined locally, but no
# attempt to obtain them is made until the generic function is called.

# Binary operator functions.

def add(a, b):
    if is_int(a) and is_int(b):
        return int_add(a, b)
    return binary_op(a, b, lambda a: a.__add__, lambda b: b.__radd__)

def and_(a, b):
    if is_int(a) and is_int(b):
        return int_and(a, b)
    return binary_op(a, b, lambda a: a.__and__, lambda b: b.__rand__)

def contains(a, b):
    return in_(b, a)

def div(a, b):
    if is_int(a) and is_int(b):
        return int_div(a, b)
    return binary_op(a, b, lambda a: a.__div__, lambda b: b.__rdiv__)

def floordiv(a, b):
    return binary_op(a, b, lambda a: a.__floordiv__, lambda b: b.__rfloordiv__)

def in_(a, b):
    return b.__contains__(a)

def not_in(a, b):
    return not b.__contains__(a)

def lshift(a, b):
    return binary_op(a, b, lambda a: a.__lshift__, lambda b: b.__rlshift__)

def mod(a, b):
    if is_int(a) and is_int(b):
        return int_mod(a, b)
    return binary_op(a, b, lambda a: a.__mod__, lambda b: b.__rmod__)

def mul(a, b):
    if is_int(a) and is_int(b):
        return int_mul(a, b)
    return binary_op(a, b, lambda a: a.__mul__, lambda b: b.__rmul__)

def or_(a, b):
    if is_int(a) and is_int(b):
        return int_or(a, b)
    return binary_op(a, b, lambda a: a.__or__, lambda b: b.__ror__)

def pow(a, b):
    if is_int(a) and is_int(b):
        return int_pow(a, b)
    return binary_op(a, b, lambda a: a.__pow__, lambda b: b.__rpow__)

def rshift(a, b):
    return binary_op(a, b, lambda a: a.__rshift__, lambda b: b.__rrshift__)

def sub(a, b):
    if is_int(a) and is_int(b):
        return int_sub(a, b)
    return binary_op(a, b, lambda a: a.__sub__, lambda b: b.__rsub__)

def xor(a, b):
    if is_int(a) and is_int(b):
        return int_xor(a, b)
    return binary_op(a, b, lambda a: a.__xor__, lambda b: b.__rxor__)

# vim: tabstop=4 expandtab shiftwidth=4

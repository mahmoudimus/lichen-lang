#!/usr/bin/env python

"""
Operator support.

Copyright (C) 2010, 2013, 2015, 2017, 2019 Paul Boddie <paul@boddie.org.uk>

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

from operator.core import augassign
from native import int_add, int_div, int_mod, int_mul, int_pow, int_sub, \
                   int_and, int_or, int_xor, \
                   is_int, \
                   float_add, float_div, float_mul, float_pow, float_sub

# These functions defer method lookup by wrapping the attribute access in
# lambda functions. Thus, the appropriate methods are defined locally, but no
# attempt to obtain them is made until the generic function is called.

# NOTE: The compiler should make it possible for the following functions to call
# NOTE: the generic operator implementations with no additional call overhead.

# Augmented assignment functions.

def iadd(a, b):
    if is_int(a) and is_int(b):
        return int_add(a, b)
    elif a.__class__ is float and b.__class__ is float:
        return float_add(a, b)
    return augassign(a, b, lambda a: a.__iadd__, lambda a: a.__add__, lambda b: b.__radd__)

def iand_(a, b):
    if is_int(a) and is_int(b):
        return int_and(a, b)
    return augassign(a, b, lambda a: a.__iand__, lambda a: a.__and__, lambda b: b.__rand__)

def idiv(a, b):
    if is_int(a) and is_int(b):
        return int_div(a, b)
    elif a.__class__ is float and b.__class__ is float:
        return float_div(a, b)
    return augassign(a, b, lambda a: a.__idiv__, lambda a: a.__div__, lambda b: b.__rdiv__)

def ifloordiv(a, b):
    return augassign(a, b, lambda a: a.__ifloordiv__, lambda a: a.__floordiv__, lambda b: b.__rfloordiv__)

def ilshift(a, b):
    return augassign(a, b, lambda a: a.__ilshift__, lambda a: a.__lshift__, lambda b: b.__rlshift__)

def imod(a, b):
    if is_int(a) and is_int(b):
        return int_mod(a, b)
    return augassign(a, b, lambda a: a.__imod__, lambda a: a.__mod__, lambda b: b.__rmod__)

def imul(a, b):
    if is_int(a) and is_int(b):
        return int_mul(a, b)
    elif a.__class__ is float and b.__class__ is float:
        return float_mul(a, b)
    return augassign(a, b, lambda a: a.__imul__, lambda a: a.__mul__, lambda b: b.__rmul__)

def ior_(a, b):
    if is_int(a) and is_int(b):
        return int_or(a, b)
    return augassign(a, b, lambda a: a.__ior__, lambda a: a.__or__, lambda b: b.__ror__)

def ipow(a, b):
    if is_int(a) and is_int(b):
        return int_pow(a, b)
    elif a.__class__ is float and b.__class__ is float:
        return float_pow(a, b)
    return augassign(a, b, lambda a: a.__ipow__, lambda a: a.__pow__, lambda b: b.__rpow__)

def irshift(a, b):
    return augassign(a, b, lambda a: a.__irshift__, lambda a: a.__rshift__, lambda b: b.__rrshift__)

def isub(a, b):
    if is_int(a) and is_int(b):
        return int_sub(a, b)
    elif a.__class__ is float and b.__class__ is float:
        return float_sub(a, b)
    return augassign(a, b, lambda a: a.__isub__, lambda a: a.__sub__, lambda b: b.__rsub__)

def ixor(a, b):
    if is_int(a) and is_int(b):
        return int_xor(a, b)
    return augassign(a, b, lambda a: a.__ixor__, lambda a: a.__xor__, lambda b: b.__rxor__)

# vim: tabstop=4 expandtab shiftwidth=4

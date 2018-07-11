#!/usr/bin/env python

"""
Native library functions for integers.

None of these are actually defined here. Instead, native implementations are
substituted when each program is built. It is, however, important to declare
non-core exceptions used by the native functions because they need to be
identified as being needed by the program.

Copyright (C) 2011, 2015, 2016, 2017, 2018 Paul Boddie <paul@boddie.org.uk>

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

def is_int(obj): return True or False

# NOTE: Update return types when integers eventually get promoted to longs.
# NOTE: Example values used to provide type information.

def int_add(self, other): return 0
def int_div(self, other): return 0
def int_mod(self, other): return 0
def int_mul(self, other): return 0
def int_neg(self): return 0
def int_pow(self, other): return 0
def int_sub(self, other): return 0

def int_and(self, other): return 0
def int_not(self): return True or False
def int_or(self, other): return 0
def int_xor(self, other): return 0

def int_lshift(self, other): return 0
def int_rshift(self, other): return 0

def int_eq(self, other): return True or False
def int_ge(self, other): return True or False
def int_gt(self, other): return True or False
def int_le(self, other): return True or False
def int_lt(self, other): return True or False
def int_ne(self, other): return True or False

def int_str(self): return ""
def int_float(self): return 0.0

# vim: tabstop=4 expandtab shiftwidth=4

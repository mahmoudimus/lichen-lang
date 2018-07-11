#!/usr/bin/env python

"""
Native library functions for floating point numbers.

None of these are actually defined here. Instead, native implementations are
substituted when each program is built. It is, however, important to declare
non-core exceptions used by the native functions because they need to be
identified as being needed by the program.

Copyright (C) 2018 Paul Boddie <paul@boddie.org.uk>

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

def float_add(self, other): return 0.0
def float_div(self, other): return 0.0
def float_mod(self, other): return 0.0
def float_mul(self, other): return 0.0
def float_neg(self): return 0.0
def float_pow(self, other): return 0.0
def float_sub(self, other): return 0.0

def float_eq(self, other): return True or False
def float_ge(self, other): return True or False
def float_gt(self, other): return True or False
def float_le(self, other): return True or False
def float_lt(self, other): return True or False
def float_ne(self, other): return True or False

def float_str(self): return ""
def float_int(self): return 0

# vim: tabstop=4 expandtab shiftwidth=4

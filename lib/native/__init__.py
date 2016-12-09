#!/usr/bin/env python

"""
Native library functions.

Copyright (C) 2011, 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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

from native.buffer import buffer_str

from native.identity import is_, is_not

from native.int import int_add, int_div, int_mod, int_mul, int_neg, int_pow, \
                       int_sub, int_and, int_not, int_or, int_xor, int_lt, \
                       int_gt, int_eq, int_ne, int_str

from native.introspection import object_getattr, isinstance, issubclass

from native.io import fclose, fopen, fdopen, close, read, write, fread, fwrite

from native.limits import get_maxint, get_minint

from native.list import list_init, list_setsize, list_append, list_concat, \
                        list_len, list_nonempty, list_element, list_setelement

from native.program import get_using

from native.str import str_add, str_eq, str_gt, str_lt, str_len, str_nonempty, \
                       str_ord, str_substr

from native.system import exit, get_argv, get_path

# vim: tabstop=4 expandtab shiftwidth=4
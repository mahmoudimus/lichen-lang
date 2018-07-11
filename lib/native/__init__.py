#!/usr/bin/env python

"""
Native library functions.

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

from native.buffer import buffer_str

from native.float import float_add, float_div, float_mod, float_mul, \
                         float_neg, float_pow, float_sub, \
                         float_eq, float_ge, float_gt, float_le, float_lt, \
                         float_ne, \
                         float_int, float_str

from native.identity import is_, is_not

from native.int import int_add, int_div, int_mod, int_mul, int_neg, int_pow, \
                       int_sub, int_and, int_not, int_or, int_xor, \
                       int_lshift, int_rshift, \
                       int_eq, int_ge, int_gt, int_le, int_lt, int_ne, \
                       int_float, int_str, is_int

from native.introspection import object_getattr, isinstance, issubclass

from native.iconv import iconv, iconv_close, iconv_open, iconv_reset

from native.io import fclose, fflush, fopen, fdopen, close, read, write, fread, fwrite

from native.limits import get_maxint, get_minint

from native.list import list_init, list_setsize, list_append, list_concat, \
                        list_len, list_nonempty, list_element, list_setelement

from native.locale import getlocale, setlocale

from native.program import get_using

from native.str import str_add, str_chr, str_eq, str_gt, str_lt, \
                       str_ord, str_substr

from native.system import exit, get_argv, get_path

from native.tuple import tuple_init

from native.unicode import unicode_len, unicode_ord, unicode_substr, unicode_unichr

# vim: tabstop=4 expandtab shiftwidth=4

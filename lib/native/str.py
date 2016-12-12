#!/usr/bin/env python

"""
Native library functions for strings.

None of these are actually defined here. Instead, native implementations are
substituted when each program is built. It is, however, important to declare
non-core exceptions used by the native functions because they need to be
identified as being needed by the program.

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

# String operations.

def str_add(data, other_data): pass
def str_eq(data, other_data): pass
def str_gt(data, other_data): pass
def str_lt(data, other_data): pass
def str_len(data): pass
def str_nonempty(data): pass
def str_ord(data): pass
def str_substr(data, start, end, step): pass

# vim: tabstop=4 expandtab shiftwidth=4

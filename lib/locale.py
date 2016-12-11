#!/usr/bin/env python

"""
Locale functions.

Copyright (C) 2016 Paul Boddie <paul@boddie.org.uk>

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

from __builtins__.types import check_int, check_string
from native import getlocale as _getlocale, setlocale as _setlocale

LC_CTYPE = 0
LC_NUMERIC = 1
LC_TIME = 2
LC_COLLATE = 3
LC_MONETARY = 4
LC_MESSAGES = 5
LC_ALL = 6

def setlocale(category, value):

    "Set the locale for 'category' to 'value'."

    check_int(category)
    check_string(value)
    return _setlocale(category, value)

def getlocale(category=LC_CTYPE):

    "Return the locale value for 'category'."

    check_int(category)
    return _getlocale(category)

def initlocale(category=LC_CTYPE):

    "Initialise the locale for 'category' from the environment."

    check_int(category)
    return _setlocale(category, "")

# vim: tabstop=4 expandtab shiftwidth=4

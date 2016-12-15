#!/usr/bin/env python

"""
Unicode exception objects.

Copyright (C) 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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

class UnicodeDecodeError(Exception):

    """
    An exception indicating a failure to interpret a byte sequence according to
    a character encoding.
    """

    def __init__(self, value):

        """
        Initialise an exception with a 'value' providing the illegal byte
        sequence responsible for the error.
        """

        self.value = value

class UnicodeEncodeError(Exception): pass
class UnicodeError(Exception): pass
class UnicodeTranslateError(Exception): pass
class UnicodeWarning(Warning): pass

# vim: tabstop=4 expandtab shiftwidth=4

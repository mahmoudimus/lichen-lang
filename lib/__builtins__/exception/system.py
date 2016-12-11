#!/usr/bin/env python

"""
System exception objects.

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

class EnvironmentError(Exception): pass

class OSError(Exception):

    "A general operating system error."

    def __init__(self, value, arg):

        "Initialise the exception with the given error 'value' and 'arg'."

        self.value = value
        self.arg = arg

class RuntimeError(Exception): pass
class RuntimeWarning(Warning): pass
class SystemError(Exception): pass
class SystemExit(Exception): pass

# vim: tabstop=4 expandtab shiftwidth=4

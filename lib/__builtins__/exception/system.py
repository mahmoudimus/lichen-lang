#!/usr/bin/env python

"""
System exception objects.

Copyright (C) 2015, 2016, 2017, 2018 Paul Boddie <paul@boddie.org.uk>

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

class EnvironmentError(Exception):

    "The base class for external errors."

    pass

class OSError(Exception):

    "A general operating system error."

    def __init__(self, .value, .arg):

        "Initialise the exception with the given error 'value' and 'arg'."

        pass

    def __str__(self):
        return str(buffer(["OSError(", repr(self.value), ", ", repr(self.arg), ")"]))

    __repr__ = __str__

class SystemError(Exception):

    "A non-serious error occurring within the runtime system."

    pass

class SystemExit(Exception):

    "An exception exiting the program."

    def __init__(self, .value):

        "Initialise the exception with the given 'value'."

        pass

# vim: tabstop=4 expandtab shiftwidth=4

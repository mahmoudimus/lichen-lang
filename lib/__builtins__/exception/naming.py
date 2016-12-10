#!/usr/bin/env python

"""
Name-related exception objects.

Errors regarding unrecognised names or import failures are not provided since
these errors should occur during program compilation.

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

class AttributeError(Exception):

    "An error indicating an invalid attribute for an object."

    def __init__(self, name):

        "Initialise the exception with the given 'name'."

        self.name = name

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"""
Boolean objects.

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

class boolean:

    "The type of the True and False objects."

    def __bool__(self):

        "Identity operation."

        return self

    def __str__(self):

        "Return a string representation."

        return self is True and "True" or "False"

    __repr__ = __str__

False = boolean()
True = boolean()

def bool(obj):

    "Evaluate 'obj' as a boolean value."

    return obj.__bool__()

# vim: tabstop=4 expandtab shiftwidth=4

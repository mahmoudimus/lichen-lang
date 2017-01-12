#!/usr/bin/env python

"""
Attribute-related functions.

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

from __builtins__.types import check_string
from native import object_getattr

_default=object() # a unique placeholder for a missing value

def getattr(obj, name, default=_default):

    """
    Return for 'obj' the attribute having the given 'name', returning the given
    'default' if the attribute is not defined for 'obj', raising an exception if
    'default' is not indicated and the attribute is not defined.
    """

    check_string(name)

    # Attempt to obtain the attribute. If the name is not recognised as an
    # attribute name, the default will be returned. Otherwise, an access
    # operation will be attempted.

    try:
        result = object_getattr(obj, name, default)

    # Handle exceptions when the access operation fails.

    except TypeError:
        result = _default

    # Check the result and, if it is the placeholder value, raise an exception.

    if result is _default:
        raise AttributeError(name)

    # Otherwise, return the obtained value or supplied default.

    else:
        return result

def hasattr(obj, name):

    "Return whether 'obj' has an attribute called 'name'."

    try:
        getattr(obj, name)
    except AttributeError:
        return False
    else:
        return True

# NOTE: setattr would probably only be supported on instances due to deductions
# NOTE: applying to static objects being undermined by dynamic modifications.

def setattr(obj, name, value):
    raise NotImplementedError, "setattr"

# vim: tabstop=4 expandtab shiftwidth=4

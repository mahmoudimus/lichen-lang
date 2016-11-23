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

from native import _object_getattr

_default=object() # a unique placeholder for a missing value

def _getattr(obj, name, default=_default):

    """
    Return for 'obj' the attribute having the given 'name', returning the given
    'default' if the attribute is not defined for 'obj'.
    """

    return _object_getattr(obj, name, default)

def getattr(obj, name, default=_default):

    """
    Return for 'obj' the attribute having the given 'name', returning the given
    'default' if the attribute is not defined for 'obj', raising an exception if
    'default' is not indicated and the attribute is not defined.
    """

    result = _getattr(obj, name, default)

    if result is _default:
        if default is _default:
            raise AttributeError(name)
        else:
            return default
    else:
        return result

def hasattr(obj, name):

    "Return whether 'obj' has an attribute called 'name'."

    result = _getattr(obj, name)
    return result is not _default

def setattr(obj, name, value): pass

# vim: tabstop=4 expandtab shiftwidth=4

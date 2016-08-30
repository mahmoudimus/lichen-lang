#!/usr/bin/env python

"""
Attribute-related functions.

Copyright (C) 2015 Paul Boddie <paul@boddie.org.uk>

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

_getattr_default=object() # a unique placeholder for a missing value

def getattr(obj, name, default=_getattr_default):

    "Implementation of getattr."

    try:
        return _getattr(obj, name)
    except AttributeError:
        if default is not _getattr_default:
            return default
        else:
            raise

def hasattr(obj, name): pass
def setattr(obj, name, value): pass
def _getattr(obj, name): pass

# vim: tabstop=4 expandtab shiftwidth=4

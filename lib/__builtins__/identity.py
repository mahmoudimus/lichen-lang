#!/usr/bin/env python

"""
Identity-related functions.

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

from native import _isinstance

def callable(obj): pass
def help(*args): pass
def id(obj): pass

def isinstance(obj, cls_or_tuple):

    """
    Return whether 'obj' is an instance of 'cls_or_tuple', where the latter is
    either a class or a tuple of classes.
    """

    # NOTE: CPython insists on tuples, but any sequence might be considered
    # NOTE: acceptable.

    if _isinstance(cls_or_tuple, tuple):
        for cls in cls_or_tuple:
            if obj.__class__ is cls or _isinstance(obj, cls):
                return True
        return False
    else:
        return obj.__class__ is cls_or_tuple or _isinstance(obj, cls_or_tuple)

def issubclass(obj, cls_or_tuple): pass

def repr(obj):

    "Return a program representation for 'obj'."

    return obj.__repr__()

# vim: tabstop=4 expandtab shiftwidth=4

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

from native import _isinstance, _issubclass

def callable(obj):

    "Return whether 'obj' is callable."

    # NOTE: Classes and functions are callable, modules are not callable,
    # NOTE: only instances with __call__ methods should be callable.

    pass

def help(*args):

    # NOTE: This should show any docstring, but it is currently unsupported.

    pass

def id(obj):

    # NOTE: This should show an object's address, but it is currently
    # NOTE: unsupported.

    pass

def isclass(obj):

    "Return whether 'obj' is a class."

    return obj.__class__ is type

def isinstance(obj, cls_or_tuple):

    """
    Return whether 'obj' is an instance of 'cls_or_tuple', where the latter is
    either a class or a sequence of classes.
    """

    if _isinstance(cls_or_tuple, tuple):
        for cls in cls_or_tuple:
            if obj.__class__ is cls or isclass(cls) and _isinstance(obj, cls):
                return True
        return False
    else:
        return obj.__class__ is cls_or_tuple or isclass(cls_or_tuple) and _isinstance(obj, cls_or_tuple)

def issubclass(obj, cls_or_tuple):

    """
    Return whether 'obj' is a class that is a subclass of 'cls_or_tuple', where
    the latter is either a class or a sequence of classes. If 'obj' is the same
    as the given class or classes, True is also returned.
    """

    if not isclass(obj):
        return False
    elif _isinstance(cls_or_tuple, tuple):
        for cls in cls_or_tuple:
            if obj is cls or isclass(cls) and _issubclass(obj, cls):
                return True
        return False
    else:
        return obj is cls_or_tuple or isclass(cls_or_tuple) and _issubclass(obj, cls_or_tuple)

def repr(obj):

    "Return a program representation for 'obj'."

    # Classes do not provide __repr__ directly.

    if isclass(obj):
        return obj.__name__

    # Class attributes of instances provide __repr__.

    else:
        return obj.__repr__()

# vim: tabstop=4 expandtab shiftwidth=4

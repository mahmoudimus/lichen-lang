#!/usr/bin/env python

"""
Core objects.

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

class object:

    "The root class of all objects except functions."

    def __init__(self):
        "No-operation."
        pass

    def __bool__(self):
        "Objects are true by default."
        return True

class function:

    """
    The class of all function objects.
    Note that as a special case, function does not inherit from object.
    """

    def __init__(self):

        """
        Reserve special attributes for function instances.
        """

        self.__fn__ = None
        self.__args__ = None

    def __bool__(self):
        "Functions are true by default."
        return True

class type(object):

    "The class of all classes."

    pass

class BaseException(object): pass
class Exception(BaseException): pass
class Warning(object): pass

# vim: tabstop=4 expandtab shiftwidth=4

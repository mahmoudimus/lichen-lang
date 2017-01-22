#!/usr/bin/env python

"""
Core objects.

Copyright (C) 2015, 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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

from native import get_using

class object:

    "The root class of all objects except functions."

    def __init__(self):

        "No-operation."

        pass

    def __bool__(self):

        "Objects are true by default."

        return True

    def __str__(self):

        "Return a string representation."

        # The string representation of the class should be provided by the
        # type.__str__ method using the class as self.

        return str(buffer(["<", self.__class__, " instance>"]))

    __repr__ = __str__

class module:

    "The class of module objects."

    def __init__(self):

        """
        Reserve special attributes for module instances.
        """

        self.__file__ = None
        self.__name__ = None

    def __str__(self):

        "Return a string representation."

        return self.__name__

    __repr__ = __str__

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
        self.__name__ = None
        self.__parent__ = None

    def __bool__(self):

        "Functions are true by default."

        return True

    def __str__(self):

        "Return a string representation."

        # Combine the function's parent representation with the function's name.

        return str(buffer([self.__parent__, ".", self.__name__]))

    __repr__ = __str__

class type:

    """
    The class of all classes. Methods of this class do not treat contexts as
    instances, even though classes are meant to be instances of this class.
    Instead, contexts are either classes or instances.
    """

    def __str__(self):

        "Return a string representation."

        # With the class as self, combine the class's parent representation with
        # the class's name.

        return str(buffer([self.__parent__, ".", self.__name__]))

    __repr__ = __str__

class Exception:

    "The root of all exception types."

    pass

# Fundamental exceptions 

class MemoryError(Exception):

    "An error indicating failure to allocate or manage memory."

    pass

class TypeError(Exception):

    "An error indicating unsuitable type usage."

    pass

class UnboundMethodInvocation(Exception):

    "An error indicating an attempt to call an unbound method."

    pass

class ArithmeticError(Exception):

    "A general arithmetic operation error."

    pass

class FloatingPointError(Exception):

    "A floating point operation error."

    pass

class OverflowError(ArithmeticError):

    """
    Indicates that an arithmetic operation produced a result that could not be
    represented.
    """

    pass

class ZeroDivisionError(ArithmeticError):

    "An error occurring when an attempt was made to divide an operand by zero."

    pass

# vim: tabstop=4 expandtab shiftwidth=4

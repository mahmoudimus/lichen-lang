#!/usr/bin/env python

"""
Operator support.

Copyright (C) 2010, 2013, 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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

# Define "is" and "is not" in terms of native operations. They are imported by
# the operator.binary module.

from native import _is as is_, _is_not as is_not

def binary_op(a, b, left_accessor, right_accessor):

    """
    A single parameterised function providing the binary operator mechanism for
    arguments 'a' and 'b' using accessors given as 'left_accessor' and
    'right_accessor' which provide the methods for the operands.
    """

    # First, try and get a method for the left argument, and then call it with
    # the right argument.

    try:
        fn = left_accessor(a)
    except AttributeError:
        pass
    else:
        result = fn(b)
        if is_not(result, NotImplemented):
            return result

    # Otherwise, try and get a method for the right argument, and then call it
    # with the left argument.

    try:
        fn = right_accessor(b)
    except AttributeError:
        pass
    else:
        result = fn(a)
        if is_not(result, NotImplemented):
            return result

    # Where no methods were available, or if neither method could support the
    # operation, raise an exception.

    raise TypeError

def unary_op(a, accessor):

    """
    A single parameterised function providing the unary operator mechanism for
    the argument 'a' using the given 'accessor' to provide the method for the
    operand.
    """

    # First, try and get a method for the argument, and then call it.

    try:
        fn = accessor(a)
    except AttributeError:
        pass
    else:
        result = fn()
        if is_not(result, NotImplemented):
            return result

    # Where no method was available, or if the method could not support the
    # operation, raise an exception.

    raise TypeError

def augassign(a, b, augmented_accessor, left_accessor, right_accessor):

    """
    A single parameterised function providing the augmented assignment mechanism
    for arguments 'a' and 'b' either using 'augmented_accessor' (directly
    affecting 'a') or using 'left_accessor' and 'right_accessor' (conventional
    operator method accessors).

    The result of the assignment is returned.
    """

    # First, try and get a method that directly affects the assignment target.

    try:
        fn = augmented_accessor(a)
    except AttributeError:
        pass
    else:
        result = fn(b)
        if is_not(result, NotImplemented):
            return result

    # Otherwise, attempt a conventional binary operation.

    return binary_op(a, b, left_accessor, right_accessor)

# vim: tabstop=4 expandtab shiftwidth=4

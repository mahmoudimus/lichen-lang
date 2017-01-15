#!/usr/bin/env python

"""
Integer objects.

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

from __builtins__.operator import _negate
from __builtins__.unicode import utf8string
from native import isinstance as _isinstance, get_maxint, get_minint, \
                   int_add, int_and, int_div, int_eq, int_gt, int_lt, int_mod, \
                   int_mul, int_ne, int_neg, int_not, int_or, int_pow, \
                   int_str, int_sub, int_xor

class int:

    "An integer abstraction."

    def __init__(self, number_or_string=None):

        "Initialise the integer with the given 'number_or_string'."

        if _isinstance(number_or_string, int):
            self.__data__ = number_or_string.__data__
        else:
            # NOTE: To be implemented.
            self.__data__ = None

    def __hash__(self):

        "Return a value for hashing purposes."

        return self

    def _binary_op(self, op, other):

        "Perform 'op' on this int and 'other' if appropriate."

        if _isinstance(other, int):
            return op(self.__data__, other.__data__)
        else:
            return NotImplemented

    def _binary_op_rev(self, op, other):

        "Perform 'op' on 'other' and this int if appropriate."

        if _isinstance(other, int):
            return op(other.__data__, self.__data__)
        else:
            return NotImplemented

    def __iadd__(self, other):

        "Return a new int for the addition of this int and 'other'."

        return self._binary_op(int_add, other)

    def __isub__(self, other):

        "Return a new int for the subtraction of this int and 'other'."

        return self._binary_op(int_sub, other)

    def __imul__(self, other):

        "Return a new int for the multiplication of this int and 'other'."

        return self._binary_op(int_mul, other)

    def __idiv__(self, other):

        "Return a new int for the division of this int and 'other'."

        return self._binary_op(int_div, other)

    def __imod__(self, other):

        "Return a new int for the modulo of this int by 'other'."

        return self._binary_op(int_mod, other)

    def __ipow__(self, other):

        "Return a new int for the exponentiation of this int by 'other'."

        return self._binary_op(int_pow, other)

    def __iand__(self, other):

        "Return a new int for the binary-and of this int and 'other'."

        return self._binary_op(int_and, other)

    def __ior__(self, other):

        "Return a new int for the binary-or of this int and 'other'."

        return self._binary_op(int_or, other)

    def __ixor__(self, other):

        "Return a new int for the exclusive-or of this int and 'other'."

        return self._binary_op(int_xor, other)

    def __invert__(self):

        "Return the inversion of this int."

        return int_not(self.__data__)

    __add__ = __radd__ = __iadd__
    __sub__ = __isub__

    def __rsub__(self, other):

        "Return a new int for the subtraction of this int from 'other'."

        return self._binary_op_rev(int_sub, other)

    __mul__ = __rmul__ = __imul__
    __div__ = __idiv__

    def __rdiv__(self, other):

        "Return a new int for the division of this int into 'other'."

        return self._binary_op_rev(int_div, other)

    def __floordiv__(self, other): pass
    def __rfloordiv__(self, other): pass
    def __ifloordiv__(self, other): pass

    __mod__ = __imod__

    def __rmod__(self, other):

        "Return a new int for the modulo of 'other' by this int."

        return self._binary_op_rev(int_mod, other)

    __pow__ = __ipow__

    def __rpow__(self, other):

        "Return a new int for the exponentiation of 'other' by this int."

        return self._binary_op_rev(int_pow, other)

    __and__ = __rand__ = __iand__
    __or__ = __ror__ = __ior__
    __xor__ = __rxor__ = __ixor__

    def __lt__(self, other):

        "Return whether this int is less than 'other'."

        return self._binary_op(int_lt, other)

    def __gt__(self, other):

        "Return whether this int is greater than 'other'."

        return self._binary_op(int_gt, other)

    def __le__(self, other):

        "Return whether this int is less than or equal to 'other'."

        return _negate(self.__gt__(other))

    def __ge__(self, other):

        "Return whether this int is greater than or equal to 'other'."

        return _negate(self.__lt__(other))

    def __eq__(self, other):

        "Return whether this int is equal to 'other'."

        return self._binary_op(int_eq, other)

    def __ne__(self, other):

        "Return whether this int is not equal to 'other'."

        return _negate(self.__eq__(other))

    def __neg__(self):

        "Apply the unary negation operator."

        return int_neg(self.__data__)

    def __pos__(self):

        "Apply the unary positive operator."

        return self

    def __str__(self):

        "Return a string representation."

        return utf8string(int_str(self.__data__))

    __repr__ = __str__

    def __lshift__(self): pass
    def __rlshift__(self): pass
    def __rshift__(self): pass
    def __rrshift__(self): pass
    def __ilshift__(self): pass
    def __irshift__(self): pass

    def __bool__(self):

        "Return whether this int is non-zero."

        zero = 0
        return int_ne(self.__data__, zero.__data__)

# Limits.

maxint = get_maxint()
minint = get_minint()

# vim: tabstop=4 expandtab shiftwidth=4

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

from __builtins__.operator import _binary_op, _negate
import native

class int(object):

    "An integer abstraction."

    def __init__(self, number_or_string=None):

        "Initialise the integer with the given 'number_or_string'."

        if isinstance(number_or_string, int):
            self.__data__ = number_or_string.__data__
        else:
            # NOTE: To be implemented.
            self.__data__ = None

    def __iadd__(self, other):
        "Return a new int for the operation."
        return _binary_op(self, other, native._int_add)

    def __isub__(self, other):
        "Return a new int for the operation."
        return _binary_op(self, other, native._int_sub)

    def __imul__(self, other):
        "Return a new int for the operation."
        return _binary_op(self, other, native._int_mul)

    def __idiv__(self, other):
        "Return a new int for the operation."
        return _binary_op(self, other, native._int_div)

    def __imod__(self, other):
        "Return a new int for the operation."
        return _binary_op(self, other, native._int_mod)

    def __ipow__(self, other):
        "Return a new int for the operation."
        return _binary_op(self, other, native._int_pow)

    def __iand__(self, other):
        "Return a new int for the operation."
        return _binary_op(self, other, native._int_and)

    def __ior__(self, other):
        "Return a new int for the operation."
        return _binary_op(self, other, native._int_or)

    def __ixor__(self, other):
        "Return a new int for the operation."
        return _binary_op(self, other, native._int_xor)

    __add__ = __radd__ = __iadd__
    __sub__ = __isub__

    def __rsub__(self, other):
        "Return a new int for the operation."
        return _binary_op(other, self, native._int_sub)

    __mul__ = __rmul__ = __imul__
    __div__ = __idiv__

    def __rdiv__(self, other):
        "Return a new int for the operation."
        return _binary_op(other, self, native._int_div)

    def __floordiv__(self, other): pass
    def __rfloordiv__(self, other): pass
    def __ifloordiv__(self, other): pass

    __mod__ = __imod__

    def __rmod__(self, other):
        "Return a new int for the operation."
        return _binary_op(other, self, native._int_mod)

    __pow__ = __ipow__

    def __rpow__(self, other):
        "Return a new int for the operation."
        return _binary_op(other, self, native._int_pow)

    __and__ = __rand__ = __iand__
    __or__ = __ror__ = __ior__
    __xor__ = __rxor__ = __ixor__

    def __lt__(self, other):
        "Return a new boolean for the comparison."
        return _binary_op(self, other, native._int_lt)

    def __gt__(self, other):
        "Return a new boolean for the comparison."
        return _binary_op(self, other, native._int_gt)

    def __le__(self, other):
        "Return a new boolean for the comparison."
        return _negate(self.__gt__(other))

    def __ge__(self, other):
        "Return a new boolean for the comparison."
        return _negate(self.__lt__(other))

    def __eq__(self, other):
        "Return a new boolean for the comparison."
        return _binary_op(self, other, native._int_eq)

    def __ne__(self, other):
        "Return a new boolean for the comparison."
        return _negate(self.__eq__(other))

    def __invert__(self): pass

    def __neg__(self):
        "Apply the unary negation operator."
        return native._int_neg(self)

    def __pos__(self):
        "Apply the unary positive operator."
        return self

    def __str__(self):
        "Return a string representation."
        return native._int_str(self)

    def __lshift__(self): pass
    def __rlshift__(self): pass
    def __rshift__(self): pass
    def __rrshift__(self): pass
    def __ilshift__(self): pass
    def __irshift__(self): pass

    def __bool__(self):
        "Return whether this int is non-zero."
        return native._int_ne(self, 0)

# vim: tabstop=4 expandtab shiftwidth=4

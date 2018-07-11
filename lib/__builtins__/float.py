#!/usr/bin/env python

"""
Floating point number objects.

Copyright (C) 2015, 2016, 2018 Paul Boddie <paul@boddie.org.uk>

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

from __builtins__.unicode import utf8string
from native import isinstance as _isinstance, \
                   int_float, is_int, \
                   float_add, float_div, float_eq, float_ge, float_gt, \
                   float_le, float_lt, float_mod, float_mul, float_ne, \
                   float_neg, float_pow, float_str, float_sub, 

class float:

    "A floating point number abstraction."

    def __init__(self, number_or_string=None):

        "Initialise the integer with the given 'number_or_string'."

        # NOTE: To be implemented.

        pass

    def __hash__(self):

        "Return a value for hashing purposes."

        return self

    def _binary_op(self, op, other):

        "Perform 'op' on this float and 'other' if appropriate."

        if _isinstance(other, float):
            return op(self, other)
        elif is_int(other):
            return op(self, int_float(other))
        else:
            return NotImplemented

    def _binary_op_rev(self, op, other):

        "Perform 'op' on 'other' and this float if appropriate."

        if _isinstance(other, float):
            return op(other, self)
        elif is_int(other):
            return op(int_float(other), self)
        else:
            return NotImplemented

    def __iadd__(self, other):

        "Return a new float for the addition of this float and 'other'."

        return self._binary_op(float_add, other)

    def __isub__(self, other):

        "Return a new float for the subtraction from this float of 'other'."

        return self._binary_op(float_sub, other)

    def __imul__(self, other):

        "Return a new float for the multiplication of this float and 'other'."

        return self._binary_op(float_mul, other)

    def __idiv__(self, other):

        "Return a new float for the division of this float by 'other'."

        return self._binary_op(float_div, other)

    def __imod__(self, other):

        "Return a new float for the modulo of this float by 'other'."

        return self._binary_op(float_mod, other)

    def __ipow__(self, other):

        "Return a new float for the exponentiation of this float by 'other'."

        return self._binary_op(float_pow, other)

    __add__ = __radd__ = __iadd__
    __sub__ = __isub__

    def __rsub__(self, other):

        "Return a new float for the subtraction of this float from 'other'."

        return self._binary_op_rev(float_sub, other)

    __mul__ = __rmul__ = __imul__
    __div__ = __idiv__

    def __rdiv__(self, other):

        "Return a new float for the division of 'other' by this float."

        return self._binary_op_rev(float_div, other)

    # NOTE: To be implemented.

    def __floordiv__(self, other): pass
    def __rfloordiv__(self, other): pass
    def __ifloordiv__(self, other): pass

    __mod__ = __imod__

    def __rmod__(self, other):

        "Return a new float for the modulo of 'other' by this float."

        return self._binary_op_rev(float_mod, other)

    __pow__ = __ipow__

    def __rpow__(self, other):

        "Return a new float for the exponentiation of 'other' by this float."

        return self._binary_op_rev(float_pow, other)

    def __lt__(self, other):

        "Return whether this float is less than 'other'."

        return self._binary_op(float_lt, other)

    def __gt__(self, other):

        "Return whether this float is greater than 'other'."

        return self._binary_op(float_gt, other)

    def __le__(self, other):

        "Return whether this float is less than or equal to 'other'."

        return self._binary_op(float_le, other)

    def __ge__(self, other):

        "Return whether this float is greater than or equal to 'other'."

        return self._binary_op(float_ge, other)

    def __eq__(self, other):

        "Return whether this float is equal to 'other'."

        return self._binary_op(float_eq, other)

    def __ne__(self, other):

        "Return whether this float is not equal to 'other'."

        return self._binary_op(float_ne, other)

    def __neg__(self):

        "Apply the unary negation operator."

        return float_neg(self)

    def __pos__(self):

        "Apply the unary positive operator."

        return self

    def __str__(self):

        "Return a string representation."

        return utf8string(float_str(self))

    __repr__ = __str__

    def __bool__(self):

        "Return whether this float is non-zero."

        return float_ne(self, 0)

# vim: tabstop=4 expandtab shiftwidth=4

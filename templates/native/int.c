/* Native functions for integer operations.

Copyright (C) 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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
*/

#include <math.h>   /* ceil, log10, pow */
#include <stdio.h>  /* fdopen, snprintf */
#include <errno.h>  /* errno */
#include <string.h> /* strlen */
#include "native/common.h"
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Integer operations. */

__attr __fn_native_int_is_int(__attr __self, __attr obj)
{
    return __INTEGER(obj) ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_int_int_add(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Test for overflow. */
    if (((i > 0) && (j > 0) && (i > __MAXINT - j)) ||
        ((i < 0) && (j < 0) && (i < __MININT - j)))

        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(i + j);
}

__attr __fn_native_int_int_sub(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Test for overflow. */
    if (((i < 0) && (j > 0) && (i < __MININT + j)) ||
        ((i > 0) && (j < 0) && (i > __MAXINT + j)))

        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(i - j);
}

__attr __fn_native_int_int_mul(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Test for overflow. */
    if (((i > 0) && (j > 0) && (i > __MAXINT / j)) ||
        ((i < 0) && (j < 0) && (i > __MAXINT / j)) ||
        ((i < 0) && (j > 0) && (i < __MININT / j)) ||
        ((i > 0) && (j < 0) && (j < __MININT / i)))

        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(i * j);
}

__attr __fn_native_int_int_div(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Test for division by zero or overflow. */
    if (j == 0)
        __raise_zero_division_error();
    else if ((j == -1) && (i == __MININT))
        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(i / j);
}

__attr __fn_native_int_int_mod(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Test for division by zero or overflow. */
    if (j == 0)
        __raise_zero_division_error();
    else if ((j == -1) && (i == __MININT))
        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(i % j);
}

__attr __fn_native_int_int_neg(__attr __self, __attr self)
{
    /* self interpreted as int */
    int i = __TOINT(self);

    /* Test for overflow. */
    if (i == __MININT)
        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(-i);
}

__attr __fn_native_int_int_pow(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);
    int k;

    errno = 0;
    k = (int) pow(i, j);

    /* Test for overflow. */

    if (errno == ERANGE)
        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(k);
}

__attr __fn_native_int_int_and(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i & j);
}

__attr __fn_native_int_int_not(__attr __self, __attr self)
{
    /* self interpreted as int */
    int i = __TOINT(self);

    /* Return the new integer. */
    return __new_int(~i);
}

__attr __fn_native_int_int_or(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i | j);
}

__attr __fn_native_int_int_xor(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i ^ j);
}

__attr __fn_native_int_int_le(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Return a boolean result. */
    return i <= j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_int_int_lt(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Return a boolean result. */
    return i < j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_int_int_ge(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Return a boolean result. */
    return i >= j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_int_int_gt(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Return a boolean result. */
    return i > j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_int_int_eq(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Return a boolean result. */
    return i == j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_int_int_ne(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as int */
    int i = __TOINT(self);
    int j = __TOINT(other);

    /* Return a boolean result. */
    return i != j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_int_int_str(__attr __self, __attr self)
{
    /* self interpreted as int */
    int i = __TOINT(self);

    /* Employ a buffer big enough to fit the largest integer plus an extra
       character, a minus sign, and the null terminator. */
    unsigned int n = (int) log10(__MAXINT) + 3;
    char *s = (char *) __ALLOCATE(n, sizeof(char));

    snprintf(s, n, "%d", i);

    /* Return a new string. */
    return __new_str(s, strlen(s));
}

/* Module initialisation. */

void __main_native_int()
{
}

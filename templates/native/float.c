/* Native functions for floating point operations.

Copyright (C) 2016, 2017, 2018, 2019 Paul Boddie <paul@boddie.org.uk>

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

#include <setjmp.h>
#include <signal.h>
#include <math.h>   /* pow */
#include <stdio.h>  /* snprintf */
#include <errno.h>  /* errno */
#include "native/common.h"
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Conversion of trailing data to a double-precision floating point number. */

static double __TOFLOAT(__attr attr)
{
    return __get_trailing_data(attr, __builtins___float_float);
}

/* Numeric formatting using snprintf.
   NOTE: This might be moved elsewhere and used by other types. */

static __attr format_number(double n, int size)
{
    char *s = (char *) __ALLOCATE(size, sizeof(char));
    int digits;

    /* Allocation should raise a memory error if it fails, so this loop should
       terminate via the return statement or an allocation failure. */

    while (1)
    {
        digits = snprintf(s, size, "%f", n);

        if (digits < size)
        {
            s = (char *) __REALLOCATE(s, (digits + 1) * sizeof(char));
            return __new_str(s, digits);
        }

        size = digits + 1;
        s = (char *) __REALLOCATE(s, size * sizeof(char));
    }

    return __NULL;
}

/* Floating point exception handling. */

extern jmp_buf __fpe_env;

/* Floating point operations. */

__attr __fn_native_float_float_add(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);
    int signum;

    /* Perform the operation while handling exceptions. */
    signum = setjmp(__fpe_env);
    if (!signum)
        return __new_float(i + j);

    /* Exception occurred. */
    if (signum == FPE_FLTOVF)
        __raise_overflow_error();

    return __NULL;
}

__attr __fn_native_float_float_sub(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);
    int signum;

    /* Perform the operation while handling exceptions. */
    signum = setjmp(__fpe_env);
    if (!signum)
        return __new_float(i - j);

    /* Exception occurred. */
    if (signum == FPE_FLTOVF)
        __raise_overflow_error();

    return __NULL;
}

__attr __fn_native_float_float_mul(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);
    int signum;

    /* Perform the operation while handling exceptions. */
    signum = setjmp(__fpe_env);
    if (!signum)
        return __new_float(i * j);

    /* Exception occurred. */
    if (signum == FPE_FLTOVF)
        __raise_overflow_error();
    else if (signum == FPE_FLTUND)
        __raise_underflow_error();

    return __NULL;
}

__attr __fn_native_float_float_div(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);
    int signum;

    /* Perform the operation while handling exceptions. */
    signum = setjmp(__fpe_env);
    if (!signum)
        return __new_float(i / j);

    /* Exception occurred. */
    if (signum == FPE_FLTOVF)
        __raise_overflow_error();
    else if (signum == FPE_FLTUND)
        __raise_underflow_error();
    else if (signum == FPE_FLTDIV)
        __raise_zero_division_error();

    return __NULL;
}

__attr __fn_native_float_float_mod(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);
    int signum;

    /* Perform the operation while handling exceptions. */
    signum = setjmp(__fpe_env);
    if (!signum)
        return __new_float(fmod(i, j));

    /* Exception occurred. */
    if (signum == FPE_FLTOVF)
        __raise_overflow_error();
    else if (signum == FPE_FLTDIV)
        __raise_zero_division_error();

    return __NULL;
}

__attr __fn_native_float_float_neg(__attr __self, __attr self)
{
    /* self interpreted as float */
    double i = __TOFLOAT(self);
    int signum;

    /* Perform the operation while handling exceptions. */
    signum = setjmp(__fpe_env);
    if (!signum)
        return __new_float(-i);

    /* Exception occurred. */
    if (signum == FPE_FLTOVF)
        __raise_overflow_error();

    return __NULL;
}

__attr __fn_native_float_float_pow(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);
    double result;

    errno = 0;
    result = pow(i, j);

    /* Test for overflow. */

    if (errno == ERANGE)
        __raise_overflow_error();

    /* Return the result. */
    return __new_float(result);
}

__attr __fn_native_float_float_le(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);

    /* Return a boolean result. */
    return i <= j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_float_float_lt(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);

    /* Return a boolean result. */
    return i < j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_float_float_ge(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);

    /* Return a boolean result. */
    return i >= j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_float_float_gt(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);

    /* Return a boolean result. */
    return i > j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_float_float_eq(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);

    /* Return a boolean result. */
    return i == j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_float_float_ne(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);

    /* Return a boolean result. */
    return i != j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_float_float_str(__attr __self, __attr self)
{
    /* self interpreted as float */
    double i = __TOFLOAT(self);

    /* Return a new string. */
    return format_number(i, 64);
}

__attr __fn_native_float_float_int(__attr __self, __attr self)
{
    /* self interpreted as float */
    double i = __TOFLOAT(self);

    /* NOTE: Test for conversion failure. */
    return __new_int((int) i);
}

/* Module initialisation. */

void __main_native_float()
{
}

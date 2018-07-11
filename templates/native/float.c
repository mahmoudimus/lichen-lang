/* Native functions for floating point operations.

Copyright (C) 2016, 2017, 2018 Paul Boddie <paul@boddie.org.uk>

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

#include <fenv.h>   /* feclearexcept, fetestexcept */
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

/* Conversion from a pair of consecutive attributes to a double-precision
   floating point number. */

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

static void init_env(fenv_t *envp, int excepts)
{
    fegetenv(envp);
    feclearexcept(excepts);
}

static int test_env(fenv_t *envp, int excepts)
{
    if (fetestexcept(excepts))
    {
        fesetenv(envp);
        return 1;
    }
    return 0;
}

static int have_result(fenv_t *envp, int excepts)
{
    return !fetestexcept(excepts);
}

static __attr make_result(fenv_t *envp, double result)
{
    fesetenv(envp);
    return __new_float(result);
}

/* Floating point operations. */

__attr __fn_native_float_float_add(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);
    double result;

    /* Preserve environment, clear exception state. */
    fenv_t env;
    init_env(&env, FE_OVERFLOW);

    result = i + j;

    /* Test for result, restore state, return the new float. */
    if (have_result(&env, FE_OVERFLOW))
        return make_result(&env, result);

    /* Restore state, raise exception. */
    if (test_env(&env, FE_OVERFLOW))
        __raise_overflow_error();
    return __NULL;
}

__attr __fn_native_float_float_sub(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);
    double result;

    /* Preserve environment, clear exception state. */
    fenv_t env;
    init_env(&env, FE_OVERFLOW);

    result = i - j;

    /* Test for result, restore state, return the new float. */
    if (have_result(&env, FE_OVERFLOW))
        return make_result(&env, result);

    /* Restore state, raise exception. */
    if (test_env(&env, FE_OVERFLOW))
        __raise_overflow_error();
    return __NULL;
}

__attr __fn_native_float_float_mul(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);
    double result;

    /* Preserve environment, clear exception state. */
    fenv_t env;
    init_env(&env, FE_OVERFLOW | FE_UNDERFLOW);

    result = i * j;

    /* Test for result, restore state, return the new float. */
    if (have_result(&env, FE_OVERFLOW | FE_UNDERFLOW))
        return make_result(&env, result);

    /* Restore state, raise exception. */
    if (test_env(&env, FE_OVERFLOW))
        __raise_overflow_error();
    if (test_env(&env, FE_UNDERFLOW))
        __raise_underflow_error();
    return __NULL;
}

__attr __fn_native_float_float_div(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);
    double result;

    /* Preserve environment, clear exception state. */
    fenv_t env;
    init_env(&env, FE_OVERFLOW | FE_UNDERFLOW | FE_DIVBYZERO);

    result = i / j;

    /* Test for result, restore state, return the new float. */
    if (have_result(&env, FE_OVERFLOW | FE_UNDERFLOW | FE_DIVBYZERO))
        return make_result(&env, result);

    /* Restore state, raise exception. */
    if (test_env(&env, FE_OVERFLOW))
        __raise_overflow_error();
    if (test_env(&env, FE_UNDERFLOW))
        __raise_underflow_error();
    if (test_env(&env, FE_DIVBYZERO))
        __raise_zero_division_error();
    return __NULL;
}

__attr __fn_native_float_float_mod(__attr __self, __attr self, __attr other)
{
    /* self and other interpreted as float */
    double i = __TOFLOAT(self);
    double j = __TOFLOAT(other);
    double result;

    /* Preserve environment, clear exception state. */
    fenv_t env;
    init_env(&env, FE_OVERFLOW | FE_DIVBYZERO);

    result = fmod(i, j);

    /* Test for result, restore state, return the new float. */
    if (have_result(&env, FE_OVERFLOW | FE_DIVBYZERO))
        return make_result(&env, result);

    /* Restore state, raise exception. */
    if (test_env(&env, FE_OVERFLOW))
        __raise_overflow_error();
    if (test_env(&env, FE_DIVBYZERO))
        __raise_zero_division_error();
    return __NULL;
}

__attr __fn_native_float_float_neg(__attr __self, __attr self)
{
    /* self interpreted as float */
    double i = __TOFLOAT(self);
    double result;

    /* Preserve environment, clear exception state. */
    fenv_t env;
    init_env(&env, FE_OVERFLOW);

    result = -i;

    /* Test for result, restore state, return the new float. */
    if (have_result(&env, FE_OVERFLOW))
        return make_result(&env, result);

    /* Restore state, raise exception. */
    if (test_env(&env, FE_OVERFLOW))
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

/* Native functions for string operations.

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

#include <string.h> /* strcmp, memcpy */
#include "native/common.h"
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* String operations. */

__attr __fn_native_str_str_add(__attr __self, __attr _data, __attr other, __attr _size, __attr othersize)
{
    /* _data, other interpreted as string.__data__ */
    char *s = _data.strvalue;
    char *o = other.strvalue;
    /* _size, othersize interpreted as int.__data__ */
    int ss = _size.intvalue, os = othersize.intvalue;
    int n = ss + os;
    char *r = (char *) __ALLOCATE(n + 1, sizeof(char));

    memcpy(r, s, ss);
    memcpy(r + ss, o, os);

    /* Return a new string. */
    return __new_str(r, n);
}

__attr __fn_native_str_str_chr(__attr __self, __attr _data)
{
    /* _data interpreted as int.__data__ */
    int n = _data.intvalue;
    char *s = (char *) __ALLOCATE(2, sizeof(char));

    s[0] = (char) n;
    return __new_str(s, 1);
}

__attr __fn_native_str_str_lt(__attr __self, __attr _data, __attr other)
{
    /* _data, other interpreted as string.__data__ */
    char *s = _data.strvalue;
    char *o = other.strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) < 0 ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_str_str_gt(__attr __self, __attr _data, __attr other)
{
    /* _data, other interpreted as string.__data__ */
    char *s = _data.strvalue;
    char *o = other.strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) > 0 ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_str_str_eq(__attr __self, __attr _data, __attr other)
{
    /* _data, other interpreted as string.__data__ */
    char *s = _data.strvalue;
    char *o = other.strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) == 0 ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_str_str_ord(__attr __self, __attr _data)
{
    /* _data interpreted as string.__data__ */
    char *s = _data.strvalue;

    return __new_int((unsigned int) s[0]);
}

__attr __fn_native_str_str_substr(__attr __self, __attr _data, __attr start, __attr end, __attr step)
{
    /* _data interpreted as string.__data__ */
    char *s = _data.strvalue, *sub;
    /* start interpreted as int */
    int istart = __load_via_object(start.value, __data__).intvalue;
    /* end interpreted as int */
    int iend = __load_via_object(end.value, __data__).intvalue;
    /* step interpreted as int */
    int istep = __load_via_object(step.value, __data__).intvalue;

    /* Calculate the size of the substring. */
    size_t resultsize = ((iend - istart - (istep > 0 ? 1 : -1)) / istep) + 1;
    int to, from;

    /* Reserve space for a new string. */
    sub = (char *) __ALLOCATE(resultsize + 1, sizeof(char));

    /* Does not null terminate but final byte should be zero. */
    if (istep > 0)
        for (from = istart, to = 0; from < iend; from += istep, to++)
            sub[to] = s[from];
    else if (istep < 0)
        for (from = istart, to = 0; from > iend; from += istep, to++)
            sub[to] = s[from];

    return __new_str(sub, resultsize);
}

/* Module initialisation. */

void __main_native_str()
{
}

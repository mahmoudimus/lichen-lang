/* Native functions for locale handling.

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

#include <locale.h> /* setlocale */
#include <string.h> /* strlen */
#include "native/common.h"
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Locales. */

__attr __fn_native_locale_getlocale(__attr __args[])
{
    __attr * const category = &__args[1];
    /* category interpreted as int */
    int cat = __TOINT(*category);
    char *result, *out;
    size_t length;

    result = setlocale(cat, NULL);

    if (result == NULL)
        return __builtins___none_None;

    length = strlen(result);
    out = __ALLOCATE(length + 1, sizeof(char));
    strncpy(out, result, length);

    return __new_str(result, length);
}

__attr __fn_native_locale_setlocale(__attr __args[])
{
    __attr * const category = &__args[1];
    __attr * const value = &__args[2];
    /* category interpreted as int */
    int cat = __TOINT(*category);
    /* value.__data__ interpreted as string */
    char *s = __load_via_object(__VALUE(*value), __data__).strvalue;
    char *result, *out;
    size_t length;

    result = setlocale(cat, s);

    if (result == NULL)
        return __builtins___none_None;

    length = strlen(result);
    out = __ALLOCATE(length + 1, sizeof(char));
    strncpy(out, result, length);

    return __new_str(result, length);
}

/* Module initialisation. */

void __main_native_locale()
{
}

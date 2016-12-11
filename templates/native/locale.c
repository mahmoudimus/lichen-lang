/* Native functions for locale handling.

Copyright (C) 2016 Paul Boddie <paul@boddie.org.uk>

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
    int cat = __load_via_object(category->value, __pos___data__).intvalue;
    char *result;

    result = setlocale(cat, NULL);

    if (result == NULL)
        return __builtins___none_None;
    else
        return __new_str(result);
}

__attr __fn_native_locale_setlocale(__attr __args[])
{
    __attr * const category = &__args[1];
    __attr * const value = &__args[2];
    /* category interpreted as int */
    int cat = __load_via_object(category->value, __pos___data__).intvalue;
    /* value interpreted as string */
    char *s = __load_via_object(value->value, __pos___data__).strvalue, *result;

    result = setlocale(cat, s);

    if (result == NULL)
        return __builtins___none_None;
    else
        return __new_str(result);
}

/* Module initialisation. */

void __main_native_locale()
{
}

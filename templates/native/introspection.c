/* Native functions for introspection operations.

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

#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Introspection. */

__attr __fn_native_introspection_object_getattr(__attr __args[])
{
    __attr * const obj = &__args[1];
    __attr * const name = &__args[2];
    __attr * const _default = &__args[3];
    /* name.__data__ interpreted as string */
    __attr key = __load_via_object(name->value, __key__);
    __attr out;

    if ((key.code == 0) && (key.pos == 0))
        return *_default;

    /* Attempt to get the attribute from the object. */

    out = __check_and_load_via_object_null(obj->value, key.pos, key.code);
    if (out.value == 0)
    {
        /* Inspect the object's class if this failed. */

        out = __check_and_load_via_class__(obj->value, key.pos, key.code);
        if (out.value == 0)
            return *_default;

        /* Update the context to the object if it is a method. */

        return __update_context(obj->value, out);
    }

    return out;
}

static int __issubclass(__ref obj, __attr cls)
{
    return (__HASATTR(obj, __TYPEPOS(cls.value), __TYPECODE(cls.value)));
}

__attr __fn_native_introspection_isinstance(__attr __args[])
{
    __attr * const obj = &__args[1];
    __attr * const cls = &__args[2];

    /* cls must be a class. */
    if (__is_instance(obj->value) && __issubclass(__get_class(obj->value), *cls))
        return __builtins___boolean_True;
    else
        return __builtins___boolean_False;
}

__attr __fn_native_introspection_issubclass(__attr __args[])
{
    __attr * const obj = &__args[1];
    __attr * const cls = &__args[2];

    /* obj and cls must be classes. */
    if (__issubclass(obj->value, *cls))
        return __builtins___boolean_True;
    else
        return __builtins___boolean_False;
}

/* Module initialisation. */

void __main_native_introspection()
{
}

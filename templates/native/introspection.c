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

__attr __fn_native_introspection_object_getattr(__attr __self, __attr obj, __attr name, __attr _default)
{
    /* name interpreted as string */
    __attr key = __load_via_object(__VALUE(name), __key__);
    __attr out;

    if ((key.code == 0) && (key.pos == 0))
        return _default;

    /* Attempt to get the attribute from the object. */

    out = __check_and_load_via_object_null(__VALUE(obj), key.pos, key.code);
    if (__ISNULL(out))
    {
        /* Inspect the object's class if this failed. */

        out = __check_and_load_via_class__(__VALUE(obj), key.pos, key.code);
        if (__ISNULL(out))
            return _default;

        /* Update the context to the object if it is a method. */

        return __update_context(obj, out);
    }

    return out;
}

__attr __fn_native_introspection_isinstance(__attr __self, __attr obj, __attr cls)
{
    /* cls must be a class. */
    if (__is_instance_subclass(__VALUE(obj), cls))
        return __builtins___boolean_True;
    else
        return __builtins___boolean_False;
}

__attr __fn_native_introspection_issubclass(__attr __self, __attr obj, __attr cls)
{
    /* obj and cls must be classes. */
    if (__is_subclass(__VALUE(obj), cls))
        return __builtins___boolean_True;
    else
        return __builtins___boolean_False;
}

/* Module initialisation. */

void __main_native_introspection()
{
}

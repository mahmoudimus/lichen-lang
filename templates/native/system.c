/* Native functions for system operations.

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

#include <stdlib.h> /* abs, exit */
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Environment support. */

__attr __fn_native_system_exit(__attr __args[])
{
    __attr * const status = &__args[1];

    exit(__load_via_object(status->value, __pos___data__).intvalue);
    return __builtins___none_None;
}

__attr __fn_native_system_get_argv(__attr __args[])
{
    __attr * const status = &__args[1];

    /* NOTE: To be written. */
    return __builtins___none_None;
}

__attr __fn_native_system_get_path(__attr __args[])
{
    __attr * const status = &__args[1];

    /* NOTE: To be written. */
    return __builtins___none_None;
}

/* Module initialisation. */

void __main_native_system()
{
}

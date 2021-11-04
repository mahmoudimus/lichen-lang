/* Native functions for identity operations.

Copyright (C) 2016, 2017, 2021 Paul Boddie <paul@boddie.org.uk>

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

/* Identity testing. */

__attr __fn_native_identity_is_(__attr __self, __attr x, __attr y)
{
    /* NOTE: value member assumed equivalent to rawvalue for comparison. */

    return x.value == y.value ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_identity_is_not(__attr __self, __attr x, __attr y)
{
    /* NOTE: value member assumed equivalent to rawvalue for comparison. */

    return x.value != y.value ? __builtins___boolean_True : __builtins___boolean_False;
}

/* Module initialisation. */

void __main_native_identity()
{
}

/* Native functions for limit definition.

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

#include "native/common.h"
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Limit definition. */

/* NOTE: Could have statically allocated limits. */

__attr __fn_native_limits_get_maxint(__attr __self)
{
    return __new_int(__MAXINT);
}

__attr __fn_native_limits_get_minint(__attr __self)
{
    return __new_int(__MININT);
}

/* Module initialisation. */

void __main_native_limits()
{
}

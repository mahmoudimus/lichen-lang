/* Native functions for tuple operations.

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

#include "native/common.h"
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Tuple operations. */

static __fragment __empty_fragment = {.size=0, .capacity=0};

__attr __fn_native_tuple_tuple_init(__attr __self, __attr size)
{
    /* size interpreted as int */
    int n = __TOINT(size);

    /* Return the __data__ attribute. */
    if (n) return (__attr) {.seqvalue=__new_fragment(n)};
    else return (__attr) {.seqvalue=&__empty_fragment};
}

/* Module initialisation. */

void __main_native_tuple()
{
}

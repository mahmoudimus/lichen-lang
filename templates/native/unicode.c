/* Native functions for Unicode operations.

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

#include <string.h> /* strcmp, memcpy */
#include "native/common.h"
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Unicode operations. */

__attr __fn_native_unicode_unicode_len(__attr __args[])
{
    __attr * const _data = &__args[1];
    /* _data interpreted as string */
    char *s = _data->strvalue;
    int i, c = 0;

    for (i = 0; i < _data->size; i++)
        if (((s[i] & 0xc0) == 0xc0) || !(s[i] & 0x80))
            c++;

    /* Return the new integer. */
    return __new_int(c);
}

/* Module initialisation. */

void __main_native_unicode()
{
}

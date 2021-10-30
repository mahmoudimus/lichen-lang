/* Native functions for buffer operations.

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

#include <string.h> /* strcmp, memcpy */
#include "native/common.h"
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

__attr __fn_native_buffer_buffer_str(__attr __self, __attr _data)
{
    /* _data interpreted as buffer.__data__ */
    __fragment *data = _data.seqvalue;
    __int size = 0, i, j, n;
    char *s;
    __attr o;

    /* Calculate the size of the string. */
    for (i = 0; i < data->size; i++)
        size += __TOINT(__load_via_object(__VALUE(data->attrs[i]), __size__));

    /* Reserve space for a new string. */
    s = (char *) __ALLOCATE(size + 1, sizeof(char));

    /* Build a single string from the buffer contents. */
    for (i = 0, j = 0; i < data->size; i++)
    {
        o = __load_via_object(__VALUE(data->attrs[i]), __data__);
        n = __TOINT(__load_via_object(__VALUE(data->attrs[i]), __size__));
        memcpy(s + j, o.strvalue, n); /* does not null terminate but final byte should be zero */
        j += n;
    }

    /* Return a new string. */
    return __new_str(s, size);
}

/* Module initialisation. */

void __main_native_buffer()
{
}

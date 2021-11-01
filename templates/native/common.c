/* Common operations for native functions.

Copyright (C) 2016, 2017, 2018, 2021 Paul Boddie <paul@boddie.org.uk>

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

/* Utility functions. */

__attr __new_str(char *s, __int size)
{
    /* Create a new string and mutate the __data__, __size__ and __key__ attributes. */
    __attr attr = __NEWINSTANCE(__builtins___str_str);
    __store_via_object(__VALUE(attr), __data__, (__attr) {.strvalue=s});
    __store_via_object(__VALUE(attr), __size__, __INTVALUE(size));
    __store_via_object(__VALUE(attr), __key__, __NULL);
    return attr;
}

__attr __new_list(__fragment *f)
{
    /* Create a new list and mutate the __data__ attribute. */
    __attr attr = __NEWINSTANCE(__builtins___list_list);
    __store_via_object(__VALUE(attr), __data__, (__attr) {.seqvalue=f});
    return attr;
}

__attr __new_float(double n)
{
    /* Create a new float and set the trailing data. */
    __attr attr = __NEWINSTANCEIM(__builtins___float_float);
    __set_trailing_data(attr, __builtins___float_float, n);
    return attr;
}

__fragment *__fragment_append(__fragment *data, __attr value)
{
    __fragment *newdata = data;
    __int size = data->size, capacity = data->capacity;
    __int n;

    /* Re-allocate the fragment if the capacity has been reached. */
    if (size >= capacity)
    {
        /* NOTE: Consider various restrictions on capacity increases. */
        n = capacity ? capacity * 2 : 1;
        newdata = (__fragment *) __REALLOCATE(data, __FRAGMENT_SIZE(n));
        newdata->capacity = n;
    }

    /* Insert the new element and increment the list size. */
    newdata->attrs[size] = value;
    newdata->size = size + 1;

    return newdata;
}

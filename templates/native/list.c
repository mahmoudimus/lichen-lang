/* Native functions for list operations.

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

/* List operations. */

__attr __fn_native_list_list_init(__attr __self, __attr size)
{
    /* size interpreted as int */
    __int n = __TOINT(size);
    __attr attr = {.seqvalue=__new_fragment(n)};

    /* Return the __data__ attribute. */
    return attr;
}

__attr __fn_native_list_list_setsize(__attr __self, __attr _data, __attr size)
{
    /* _data interpreted as list.__data__ */
    __fragment *data = _data.seqvalue;
    /* size interpreted as int */
    __int n = __TOINT(size);

    data->size = n;
    return __builtins___none_None;
}

__attr __fn_native_list_list_append(__attr __self, __attr self, __attr value)
{
    /* self.__data__ interpreted as list */
    __fragment *data = __load_via_object(__VALUE(self), __data__).seqvalue;
    __fragment *newdata = __fragment_append(data, value);

    /* Replace the __data__ attribute if appropriate. */
    if (newdata != data)
        __store_via_object_internal(__VALUE(self), __data__, ((__attr) {.seqvalue=newdata}));
    return __builtins___none_None;
}

__attr __fn_native_list_list_concat(__attr __self, __attr self, __attr other)
{
    /* self, interpreted as list, other interpreted as list.__data__ */
    __fragment *data = __load_via_object(__VALUE(self), __data__).seqvalue;
    __fragment *other_data = other.seqvalue;
    __fragment *newdata = data;
    __int size = data->size, capacity = data->capacity;
    __int other_size = other_data->size;
    __int i, j, n = size + other_size;

    /* Re-allocate the fragment if the capacity has been reached. */
    if (n >= capacity)
    {
        newdata = (__fragment *) __REALLOCATE(data, __FRAGMENT_SIZE(n));
        newdata->capacity = n;
    }

    /* Copy the elements from the other list and increment the list size. */
    for (i = size, j = 0; j < other_size; i++, j++)
    {
        newdata->attrs[i] = __RAWVALUE(0);
        __store_target(&newdata->attrs[i], other_data->attrs[j]);
    }

    newdata->size = n;

    /* Replace the __data__ attribute if appropriate. */
    if (newdata != data)
        __store_via_object_internal(__VALUE(self), __data__, ((__attr) {.seqvalue=newdata}));
    return __builtins___none_None;
}

__attr __fn_native_list_list_len(__attr __self, __attr _data)
{
    /* _data interpreted as list.__data__ */
    __int size = _data.seqvalue->size;

    /* Return the new integer. */
    return __new_int(size);
}

__attr __fn_native_list_list_nonempty(__attr __self, __attr _data)
{
    return _data.seqvalue->size ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_list_list_element(__attr __self, __attr _data, __attr index)
{
    /* _data interpreted as list.__data__ */
    __attr *elements = _data.seqvalue->attrs;
    /* index interpreted as int */
    __int i = __TOINT(index);

    return elements[i];
}

__attr __fn_native_list_list_setelement(__attr __self, __attr _data, __attr index, __attr value)
{
    /* _data interpreted as list.__data__ */
    __attr *elements = _data.seqvalue->attrs;
    /* index interpreted as int */
    __int i = __TOINT(index);

    /* Set the element. */
    __store_target(&elements[i], value);
    return __builtins___none_None;
}

/* Module initialisation. */

void __main_native_list()
{
}

/* Native functions for list operations.

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

/* List operations. */

__attr __fn_native_list_list_init(__attr __args[])
{
    __attr * const size = &__args[1];
    /* size.__data__ interpreted as int */
    unsigned int n = __load_via_object(size->value, __data__).intvalue;
    __attr attr = {.seqvalue=__new_fragment(n)};

    /* Return the __data__ attribute. */
    return attr;
}

__attr __fn_native_list_list_setsize(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const size = &__args[2];
    /* _data interpreted as list */
    __fragment *data = _data->seqvalue;
    /* size.__data__ interpreted as int */
    unsigned int n = __load_via_object(size->value, __data__).intvalue;

    data->size = n;
    return __builtins___none_None;
}

__attr __fn_native_list_list_append(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const value = &__args[2];
    /* self.__data__ interpreted as list */
    __fragment *data = __load_via_object(self->value, __data__).seqvalue;
    __fragment *newdata = __fragment_append(data, value);

    /* Replace the __data__ attribute if appropriate. */
    if (newdata != data)
        __store_via_object(self->value, __data__, ((__attr) {.seqvalue=newdata}));
    return __builtins___none_None;
}

__attr __fn_native_list_list_concat(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__, other interpreted as list */
    __fragment *data = __load_via_object(self->value, __data__).seqvalue;
    __fragment *other_data = other->seqvalue;
    __fragment *newdata = data;
    unsigned int size = data->size, capacity = data->capacity;
    unsigned int other_size = other_data->size;
    unsigned int i, j, n = size + other_size;

    /* Re-allocate the fragment if the capacity has been reached. */
    if (n >= capacity)
    {
        newdata = (__fragment *) __REALLOCATE(data, __FRAGMENT_SIZE(n));
        newdata->capacity = n;
    }

    /* Copy the elements from the other list and increment the list size. */
    for (i = size, j = 0; j < other_size; i++, j++)
        newdata->attrs[i] = other_data->attrs[j];
    newdata->size = n;

    /* Replace the __data__ attribute if appropriate. */
    if (newdata != data)
        __store_via_object(self->value, __data__, ((__attr) {.seqvalue=newdata}));
    return __builtins___none_None;
}

__attr __fn_native_list_list_len(__attr __args[])
{
    __attr * const _data = &__args[1];
    /* _data interpreted as fragment */
    unsigned int size = _data->seqvalue->size;

    /* Return the new integer. */
    return __new_int(size);
}

__attr __fn_native_list_list_nonempty(__attr __args[])
{
    __attr * const _data = &__args[1];

    return _data->seqvalue->size ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native_list_list_element(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const index = &__args[2];
    /* _data interpreted as fragment */
    __attr *elements = _data->seqvalue->attrs;
    /* index.__data__ interpreted as int */
    int i = __load_via_object(index->value, __data__).intvalue;

    return elements[i];
}

__attr __fn_native_list_list_setelement(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const index = &__args[2];
    __attr * const value = &__args[3];
    /* _data interpreted as fragment */
    __attr *elements = _data->seqvalue->attrs;
    /* index.__data__ interpreted as int */
    int i = __load_via_object(index->value, __data__).intvalue;

    /* Set the element. */
    elements[i] = *value;
    return __builtins___none_None;
}

/* Module initialisation. */

void __main_native_list()
{
}

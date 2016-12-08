/* Native functions.

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
#include <unistd.h> /* read, write */
#include <limits.h> /* INT_MAX, INT_MIN */
#include <math.h>   /* ceil, log10, pow */
#include <string.h> /* strcmp, strncpy, strlen */
#include <stdio.h>  /* fdopen, snprintf */
#include <errno.h>  /* errno */
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Utility functions. */

static __attr __new_int(int i)
{
    /* Create a new integer and mutate the __data__ attribute. */
    __attr attr = __new(&__InstanceTable___builtins___int_int, &__builtins___int_int, sizeof(__obj___builtins___int_int));
    attr.value->attrs[__pos___data__].intvalue = i;
    return attr;
}

static __attr __new_str(char *s)
{
    /* Create a new string and mutate the __data__ attribute. */
    __attr attr = __new(&__InstanceTable___builtins___str_string, &__builtins___str_string, sizeof(__obj___builtins___str_string));
    attr.value->attrs[__pos___data__].strvalue = s;
    return attr;
}

static __attr __new_list(__fragment *f)
{
    /* Create a new list and mutate the __data__ attribute. */
    __attr attr = __new(&__InstanceTable___builtins___list_list, &__builtins___list_list, sizeof(__obj___builtins___list_list));
    attr.value->attrs[__pos___data__].seqvalue = f;
    return attr;
}

static __fragment *__fragment_append(__fragment *data, __attr * const value)
{
    __fragment *newdata = data;
    unsigned int size = data->size, capacity = data->capacity;
    unsigned int n;

    /* Re-allocate the fragment if the capacity has been reached. */
    if (size >= capacity)
    {
        /* NOTE: Consider various restrictions on capacity increases. */
        n = capacity ? capacity * 2 : 1;
        newdata = (__fragment *) __REALLOCATE(data, __FRAGMENT_SIZE(n));
        newdata->capacity = n;
    }

    /* Insert the new element and increment the list size. */
    newdata->attrs[size] = *value;
    newdata->size = size + 1;

    return newdata;
}

/* Environment support. */

__attr __fn_native__exit(__attr __args[])
{
    __attr * const status = &__args[1];

    exit(__load_via_object(status->value, __pos___data__).intvalue);
    return __builtins___none_None;
}

__attr __fn_native__get_argv(__attr __args[])
{
    __attr * const status = &__args[1];

    /* NOTE: To be written. */
    return __builtins___none_None;
}

__attr __fn_native__get_path(__attr __args[])
{
    __attr * const status = &__args[1];

    /* NOTE: To be written. */
    return __builtins___none_None;
}

/* Identity testing. */

__attr __fn_native__is(__attr __args[])
{
    __attr * const x = &__args[1];
    __attr * const y = &__args[2];

    return x->value == y->value ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__is_not(__attr __args[])
{
    __attr * const x = &__args[1];
    __attr * const y = &__args[2];

    return x->value != y->value ? __builtins___boolean_True : __builtins___boolean_False;
}

/* Limit definition. */

__attr __fn_native__get_maxint(__attr __args[])
{
    __attr * const status = &__args[1];

    return __new_int(INT_MAX);
}

__attr __fn_native__get_minint(__attr __args[])
{
    __attr * const status = &__args[1];

    return __new_int(INT_MIN);
}

/* Integer operations. */

__attr __fn_native__int_add(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Test for overflow. */
    if (((i > 0) && (j > 0) && (i > INT_MAX - j)) ||
        ((i < 0) && (j < 0) && (i < INT_MIN - j)))

        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(i + j);
}

__attr __fn_native__int_sub(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Test for overflow. */
    if (((i < 0) && (j > 0) && (i < INT_MIN + j)) ||
        ((i > 0) && (j < 0) && (i > INT_MAX + j)))

        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(i - j);
}

__attr __fn_native__int_mul(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Test for overflow. */
    if (((i > 0) && (j > 0) && (i > INT_MAX / j)) ||
        ((i < 0) && (j < 0) && (i > INT_MAX / j)) ||
        ((i < 0) && (j > 0) && (i < INT_MIN / j)) ||
        ((i > 0) && (j < 0) && (j < INT_MIN / i)))

        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(i * j);
}

__attr __fn_native__int_div(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Test for division by zero or overflow. */
    if (j == 0)
        __raise_zero_division_error();
    else if ((j == -1) && (i == INT_MIN))
        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(i / j);
}

__attr __fn_native__int_mod(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Test for division by zero or overflow. */
    if (j == 0)
        __raise_zero_division_error();
    else if ((j == -1) && (i == INT_MIN))
        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(i % j);
}

__attr __fn_native__int_neg(__attr __args[])
{
    __attr * const _data = &__args[1];
    /* _data interpreted as int */
    int i = _data->intvalue;

    /* Test for overflow. */
    if (i == INT_MIN)
        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(-i);
}

__attr __fn_native__int_pow(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;
    int k;

    errno = 0;
    k = (int) pow(i, j);

    /* Test for overflow. */

    if (errno == ERANGE)
        __raise_overflow_error();

    /* Return the new integer. */
    return __new_int(k);
}

__attr __fn_native__int_and(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i & j);
}

__attr __fn_native__int_not(__attr __args[])
{
    __attr * const _data = &__args[1];
    /* _data interpreted as int */
    int i = _data->intvalue;

    /* Return the new integer. */
    return __new_int(~i);
}

__attr __fn_native__int_or(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i | j);
}

__attr __fn_native__int_xor(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i ^ j);
}

__attr __fn_native__int_lt(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Return a boolean result. */
    return i < j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__int_gt(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Return a boolean result. */
    return i > j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__int_eq(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Return a boolean result. */
    return i == j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__int_ne(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data and other interpreted as int */
    int i = _data->intvalue;
    int j = other->intvalue;

    /* Return a boolean result. */
    return i != j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__int_str(__attr __args[])
{
    __attr * const _data = &__args[1];
    /* _data interpreted as int */
    int i = _data->intvalue;
    /* Employ a buffer big enough to fit the largest integer plus an extra
       character, a minus sign, and the null terminator. */
    unsigned int n = (int) log10(INT_MAX) + 3;
    char *s = (char *) __ALLOCATE(n, sizeof(char));

    snprintf(s, n, "%d", i);

    /* Return a new string. */
    return __new_str(s);
}

/* String operations. */

__attr __fn_native__str_add(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data, other interpreted as string */
    char *s = _data->strvalue;
    char *o = other->strvalue;
    int n = strlen(s) + strlen(o) + 1;
    char *r = (char *) __ALLOCATE(n, sizeof(char));

    strncpy(r, s, n);
    strncpy(r + strlen(s), o, n - strlen(s)); /* should null terminate */

    /* Return a new string. */
    return __new_str(r);
}

__attr __fn_native__str_lt(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data, other interpreted as string */
    char *s = _data->strvalue;
    char *o = other->strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) < 0 ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__str_gt(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data, other interpreted as string */
    char *s = _data->strvalue;
    char *o = other->strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) > 0 ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__str_eq(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const other = &__args[2];
    /* _data, other interpreted as string */
    char *s = _data->strvalue;
    char *o = other->strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) == 0 ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__str_len(__attr __args[])
{
    __attr * const _data = &__args[1];
    /* _data interpreted as string */
    char *s = _data->strvalue;

    /* Return the new integer. */
    return __new_int(strlen(s));
}

__attr __fn_native__str_nonempty(__attr __args[])
{
    __attr * const _data = &__args[1];
    /* _data interpreted as string */
    char *s = _data->strvalue;

    return strlen(s) ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__str_ord(__attr __args[])
{
    __attr * const _data = &__args[1];
    /* _data interpreted as string */
    char *s = _data->strvalue;

    return __new_int((unsigned int) s[0]);
}

__attr __fn_native__str_substr(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const start = &__args[2];
    __attr * const size = &__args[3];
    /* _data interpreted as string */
    char *s = _data->strvalue, *sub;
    /* start.__data__ interpreted as int */
    int i = __load_via_object(start->value, __pos___data__).intvalue;
    /* size.__data__ interpreted as int */
    int l = __load_via_object(size->value, __pos___data__).intvalue;

    /* Reserve space for a new string. */
    sub = (char *) __ALLOCATE(l + 1, sizeof(char));
    strncpy(sub, s + i, l); /* does not null terminate but final byte should be zero */
    return __new_str(sub);
}

/* List operations. */

__attr __fn_native__list_init(__attr __args[])
{
    __attr * const size = &__args[1];
    /* size.__data__ interpreted as int */
    unsigned int n = __load_via_object(size->value, __pos___data__).intvalue;
    __attr attr = {0, .seqvalue=__new_fragment(n)};

    /* Return the __data__ attribute. */
    return attr;
}

__attr __fn_native__list_setsize(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const size = &__args[2];
    /* _data interpreted as list */
    __fragment *data = _data->seqvalue;
    /* size.__data__ interpreted as int */
    unsigned int n = __load_via_object(size->value, __pos___data__).intvalue;

    data->size = n;
    return __builtins___none_None;
}

__attr __fn_native__list_append(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const value = &__args[2];
    /* self.__data__ interpreted as list */
    __fragment *data = __load_via_object(self->value, __pos___data__).seqvalue;
    __fragment *newdata = __fragment_append(data, value);

    /* Replace the __data__ attribute if appropriate. */
    if (newdata != data)
        __store_via_object(self->value, __pos___data__, ((__attr) {0, .seqvalue=newdata}));
    return __builtins___none_None;
}

__attr __fn_native__list_concat(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__, other interpreted as list */
    __fragment *data = __load_via_object(self->value, __pos___data__).seqvalue;
    __fragment *other_data = other->seqvalue;
    __fragment *newdata = data;
    unsigned int size = data->size, capacity = data->capacity;
    unsigned int other_size = other_data->size;
    unsigned int i, j, n;

    /* Re-allocate the fragment if the capacity has been reached. */
    if (size + other_size >= capacity)
    {
        n = size + other_size;
        newdata = (__fragment *) __REALLOCATE(data, __FRAGMENT_SIZE(n));
        newdata->capacity = n;
    }

    /* Copy the elements from the other list and increment the list size. */
    for (i = size, j = 0; j < other_size; i++, j++)
        newdata->attrs[i] = other_data->attrs[j];
    newdata->size = n;

    /* Replace the __data__ attribute if appropriate. */
    if (newdata != data)
        __store_via_object(self->value, __pos___data__, ((__attr) {0, .seqvalue=newdata}));
    return __builtins___none_None;
}

__attr __fn_native__list_len(__attr __args[])
{
    __attr * const _data = &__args[1];
    /* _data interpreted as fragment */
    unsigned int size = _data->seqvalue->size;

    /* Return the new integer. */
    return __new_int(size);
}

__attr __fn_native__list_nonempty(__attr __args[])
{
    __attr * const _data = &__args[1];

    return _data->seqvalue->size ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__list_element(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const index = &__args[2];
    /* _data interpreted as fragment */
    __attr *elements = _data->seqvalue->attrs;
    /* index.__data__ interpreted as int */
    int i = __load_via_object(index->value, __pos___data__).intvalue;

    return elements[i];
}

__attr __fn_native__list_setelement(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const index = &__args[2];
    __attr * const value = &__args[3];
    /* _data interpreted as fragment */
    __attr *elements = _data->seqvalue->attrs;
    /* index.__data__ interpreted as int */
    int i = __load_via_object(index->value, __pos___data__).intvalue;

    /* Set the element. */
    elements[i] = *value;
    return __builtins___none_None;
}

/* Buffer operations. */

__attr __fn_native__buffer_str(__attr __args[])
{
    __attr * const _data = &__args[1];
    /* _data interpreted as buffer */
    __fragment *data = _data->seqvalue;
    unsigned int size = 0, i, j, n;
    char *s, *o;

    /* Calculate the size of the string. */
    for (i = 0; i < data->size; i++)
        size += strlen(__load_via_object(data->attrs[i].value, __pos___data__).strvalue);

    /* Reserve space for a new string. */
    s = (char *) __ALLOCATE(size + 1, sizeof(char));

    /* Build a single string from the buffer contents. */
    for (i = 0, j = 0; i < data->size; i++)
    {
        o = __load_via_object(data->attrs[i].value, __pos___data__).strvalue;
        n = strlen(o);
        strncpy(s + j, o, n); /* does not null terminate but final byte should be zero */
        j += n;
    }

    /* Return a new string. */
    return __new_str(s);
}

/* Method binding. */

__attr __fn_native__get_using(__attr __args[])
{
    __attr * const callable = &__args[1];
    __attr * const instance = &__args[2];

    return __replace_context(instance->value, *callable);
}

/* Introspection. */

__attr __fn_native__object_getattr(__attr __args[])
{
    __attr * const obj = &__args[1];
    __attr * const name = &__args[2];
    __attr * const _default = &__args[3];

    /* NOTE: To be written. */
    return __builtins___none_None;
}

static int __issubclass(__ref obj, __attr cls)
{
    return (__HASATTR(obj, __TYPEPOS(cls.value), __TYPECODE(cls.value)));
}

__attr __fn_native__isinstance(__attr __args[])
{
    __attr * const obj = &__args[1];
    __attr * const cls = &__args[2];

    /* cls must be a class. */
    if (__is_instance(obj->value) && __issubclass(__get_class(obj->value), *cls))
        return __builtins___boolean_True;
    else
        return __builtins___boolean_False;
}

__attr __fn_native__issubclass(__attr __args[])
{
    __attr * const obj = &__args[1];
    __attr * const cls = &__args[2];

    /* obj and cls must be classes. */
    if (__issubclass(obj->value, *cls))
        return __builtins___boolean_True;
    else
        return __builtins___boolean_False;
}

/* Input/output. */

__attr __fn_native__fopen(__attr __args[])
{
    __attr * const filename = &__args[1];
    __attr * const mode = &__args[2];
    /* filename.__data__ interpreted as string */
    char *fn = __load_via_object(filename->value, __pos___data__).strvalue;
    /* mode.__data__ interpreted as string */
    char *s = __load_via_object(mode->value, __pos___data__).strvalue;
    FILE *f;
    __attr attr;

    errno = 0;
    f = fopen(fn, s);

    /* Produce an exception if the operation failed. */

    if (f == NULL)
        __raise_io_error(__new_int(errno));

    /* Return the __data__ attribute. */

    else
    {
        attr.context = 0;
        attr.datavalue = (void *) f;
        return attr;
    }
}

__attr __fn_native__fdopen(__attr __args[])
{
    __attr * const fd = &__args[1];
    __attr * const mode = &__args[2];
    /* fd.__data__ interpreted as int */
    int i = __load_via_object(fd->value, __pos___data__).intvalue;
    /* mode.__data__ interpreted as string */
    char *s = __load_via_object(mode->value, __pos___data__).strvalue;
    FILE *f;
    __attr attr;

    errno = 0;
    f = fdopen(i, s);

    /* Produce an exception if the operation failed. */

    if (f == NULL)
        __raise_io_error(__new_int(errno));

    /* Return the __data__ attribute. */

    else
    {
        attr.context = 0;
        attr.datavalue = (void *) f;
        return attr;
    }
}

__attr __fn_native__fread(__attr __args[])
{
    __attr * const fp = &__args[1];
    __attr * const size = &__args[2];
    /* fp interpreted as FILE reference */
    FILE *f = (FILE *) fp->datavalue;
    /* size.__data__ interpreted as int */
    int to_read = __load_via_object(size->value, __pos___data__).intvalue;
    char buf[to_read];
    size_t have_read;
    int error;
    char *s;

    have_read = fread(buf, sizeof(char), to_read, f);

    if (have_read != to_read)
    {
        if (feof(f) && (have_read == 0))
            __raise_eof_error();
        else if (error = ferror(f))
            __raise_io_error(__new_int(error));
    }

    /* Reserve space for a new string. */

    s = __ALLOCATE(have_read + 1, sizeof(char));
    strncpy(s, (char *) buf, have_read); /* does not null terminate but final byte should be zero */
    return __new_str(s);
}

__attr __fn_native__fwrite(__attr __args[])
{
    __attr * const fp = &__args[1];
    __attr * const str = &__args[2];
    /* fp interpreted as FILE reference */
    FILE *f = (FILE *) fp->datavalue;
    /* str.__data__ interpreted as string */
    char *s = __load_via_object(str->value, __pos___data__).strvalue;
    size_t to_write = strlen(s);
    size_t have_written = fwrite(s, sizeof(char), to_write, f);
    int error;

    if (have_written != to_write)
    {
        if (feof(f))
            __raise_eof_error();
        else if (error = ferror(f))
            __raise_io_error(__new_int(error));
    }

    return __builtins___none_None;
}

__attr __fn_native__read(__attr __args[])
{
    __attr * const fd = &__args[1];
    __attr * const n = &__args[2];
    /* fd.__data__ interpreted as int */
    int i = __load_via_object(fd->value, __pos___data__).intvalue;
    /* n.__data__ interpreted as int */
    int to_read = __load_via_object(n->value, __pos___data__).intvalue;
    char buf[to_read];
    ssize_t have_read;
    char *s;

    errno = 0;
    have_read = read(i, buf, to_read * sizeof(char));

    if (have_read == -1)
        __raise_io_error(__new_int(errno));
    else
    {
        /* Reserve space for a new string. */

        s = __ALLOCATE(have_read + 1, 1);
        strncpy(s, (char *) buf, have_read); /* does not null terminate but final byte should be zero */
        return __new_str(s);
    }
}

__attr __fn_native__write(__attr __args[])
{
    __attr * const fd = &__args[1];
    __attr * const str = &__args[2];
    /* fd.__data__ interpreted as int */
    int i = __load_via_object(fd->value, __pos___data__).intvalue;
    /* str.__data__ interpreted as string */
    char *s = __load_via_object(str->value, __pos___data__).strvalue;

    write(i, s, sizeof(char) * strlen(s));
    return __builtins___none_None;
}

/* Module initialisation. */

void __main_native()
{
}

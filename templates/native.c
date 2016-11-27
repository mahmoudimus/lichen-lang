#include <stdlib.h> /* exit */
#include <unistd.h> /* read, write */
#include <math.h>   /* ceil, log10, pow */
#include <string.h> /* strcmp, strncpy, strlen */
#include <stdio.h>  /* snprintf */
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

/* Native functions. */

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

__attr __fn_native__int_add(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i + j);
}

__attr __fn_native__int_sub(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i - j);
}

__attr __fn_native__int_mul(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i * j);
}

__attr __fn_native__int_div(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i / j);
}

__attr __fn_native__int_mod(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i % j);
}

__attr __fn_native__int_neg(__attr __args[])
{
    __attr * const self = &__args[1];
    /* self.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;

    /* Return the new integer. */
    return __new_int(-i);
}

__attr __fn_native__int_pow(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int((int) pow(i, j));
}

__attr __fn_native__int_and(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i & j);
}

__attr __fn_native__int_or(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i | j);
}

__attr __fn_native__int_xor(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i ^ j);
}

__attr __fn_native__int_lt(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return a boolean result. */
    return i < j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__int_gt(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return a boolean result. */
    return i > j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__int_eq(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return a boolean result. */
    return i == j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__int_ne(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int j = __load_via_object(other->value, __pos___data__).intvalue;

    /* Return a boolean result. */
    return i != j ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__int_str(__attr __args[])
{
    __attr * const self = &__args[1];
    /* self.__data__ interpreted as int */
    int i = __load_via_object(self->value, __pos___data__).intvalue;
    int n = i != 0 ? (int) ceil(log10(i+1)) + 1 : 2;
    char *s = (char *) __ALLOCATE(n, sizeof(char));

    if (i < 0) n++;
    snprintf(s, n, "%d", i);

    /* Return a new string. */
    return __new_str(s);
}

__attr __fn_native__str_add(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__, other.__data__ interpreted as string */
    char *s = __load_via_object(self->value, __pos___data__).strvalue;
    char *o = __load_via_object(other->value, __pos___data__).strvalue;
    int n = strlen(s) + strlen(o) + 1;
    char *r = (char *) __ALLOCATE(n, sizeof(char));

    strncpy(r, s, n);
    strncpy(r + strlen(s), o, n - strlen(s));

    /* Return a new string. */
    return __new_str(r);
}

__attr __fn_native__str_lt(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__, other.__data__ interpreted as string */
    char *s = __load_via_object(self->value, __pos___data__).strvalue;
    char *o = __load_via_object(other->value, __pos___data__).strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) < 0 ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__str_gt(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__, other.__data__ interpreted as string */
    char *s = __load_via_object(self->value, __pos___data__).strvalue;
    char *o = __load_via_object(other->value, __pos___data__).strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) > 0 ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__str_eq(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__, other.__data__ interpreted as string */
    char *s = __load_via_object(self->value, __pos___data__).strvalue;
    char *o = __load_via_object(other->value, __pos___data__).strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) == 0 ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__str_len(__attr __args[])
{
    __attr * const self = &__args[1];
    /* self.__data__ interpreted as string */
    char *s = __load_via_object(self->value, __pos___data__).strvalue;

    /* Return the new integer. */
    return __new_int(strlen(s));
}

__attr __fn_native__str_nonempty(__attr __args[])
{
    __attr * const self = &__args[1];
    /* self.__data__ interpreted as string */
    char *s = __load_via_object(self->value, __pos___data__).strvalue;

    return strlen(s) ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__list_init(__attr __args[])
{
    __attr * const size = &__args[1];
    /* size.__data__ interpreted as int */
    unsigned int n = __load_via_object(size->value, __pos___data__).intvalue;

    /* Allocate space for the list. */
    __fragment *data = (__fragment *) __ALLOCATE(1, __FRAGMENT_SIZE(n));
    __attr attr = {0, .data=data};

    /* The initial capacity is the same as the given size. */
    data->size = 0;
    data->capacity = n;
    return attr;
}

__attr __fn_native__list_setsize(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const size = &__args[2];
    /* self.__data__ interpreted as list */
    __fragment *data = __load_via_object(self->value, __pos___data__).data;
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
    __fragment *data = __load_via_object(self->value, __pos___data__).data;
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

    /* Replace the __data__ attribute if appropriate. */
    if (newdata != data)
        __store_via_object(self->value, __pos___data__, ((__attr) {0, .data=newdata}));
    return __builtins___none_None;
}

__attr __fn_native__list_concat(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const other = &__args[2];
    /* self.__data__, other.__data__ interpreted as list */
    __fragment *data = __load_via_object(self->value, __pos___data__).data;
    __fragment *other_data = __load_via_object(other->value, __pos___data__).data;
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
        __store_via_object(self->value, __pos___data__, ((__attr) {0, .data=newdata}));
    return __builtins___none_None;
}

__attr __fn_native__list_len(__attr __args[])
{
    __attr * const self = &__args[1];
    /* self.__data__ interpreted as fragment */
    unsigned int size = __load_via_object(self->value, __pos___data__).data->size;

    /* Return the new integer. */
    return __new_int(size);
}

__attr __fn_native__list_nonempty(__attr __args[])
{
    __attr * const self = &__args[1];

    return __load_via_object(self->value, __pos___data__).data->size ? __builtins___boolean_True : __builtins___boolean_False;
}

__attr __fn_native__list_element(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const index = &__args[2];
    /* self.__data__ interpreted as fragment */
    __attr *elements = __load_via_object(self->value, __pos___data__).data->attrs;
    /* index.__data__ interpreted as int */
    int i = __load_via_object(index->value, __pos___data__).intvalue;

    return elements[i];
}

__attr __fn_native__list_setelement(__attr __args[])
{
    __attr * const self = &__args[1];
    __attr * const index = &__args[2];
    __attr * const value = &__args[3];
    /* self.__data__ interpreted as fragment */
    __attr *elements = __load_via_object(self->value, __pos___data__).data->attrs;
    /* index.__data__ interpreted as int */
    int i = __load_via_object(index->value, __pos___data__).intvalue;

    /* Set the element. */
    elements[i] = *value;
    return __builtins___none_None;
}

__attr __fn_native__buffer_str(__attr __args[])
{
    __attr * const self = &__args[1];
    /* self.__data__ interpreted as buffer */
    __fragment *data = __load_via_object(self->value, __pos___data__).data;
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
        strncpy(s + j, o, n);
        j += n;
    }

    /* Return a new string. */
    return __new_str(s);
}

__attr __fn_native__get_using(__attr __args[])
{
    __attr * const callable = &__args[1];
    __attr * const instance = &__args[2];

    return __replace_context(instance->value, *callable);
}

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

__attr __fn_native__read(__attr __args[])
{
    __attr * const fd = &__args[1];
    __attr * const n = &__args[2];

    /* NOTE: To be written. */
    return __builtins___none_None;
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

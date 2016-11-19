#include <stdlib.h> /* calloc, exit */
#include <unistd.h> /* read, write */
#include <math.h>   /* ceil, log10, pow */
#include <string.h> /* strcmp, strlen */
#include <stdio.h>  /* snprintf */
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Utility functions. */

inline __attr __new_int(int i)
{
    /* Create a new integer and mutate the __data__ attribute. */
    __attr attr = __new(&__InstanceTable___builtins___int_int, &__builtins___int_int, sizeof(__obj___builtins___int_int));
    attr.value->attrs[__pos___data__].intvalue = i;
    return attr;
}

inline __attr __new_str(char *s)
{
    /* Create a new string and mutate the __data__ attribute. */
    __attr attr = __new(&__InstanceTable___builtins___str_string, &__builtins___str_string, sizeof(__obj___builtins___str_string));
    attr.value->attrs[__pos___data__].strvalue = s;
    return attr;
}

/* Native functions. */

__attr __fn_native__exit(__attr __args[])
{
    #define status (__args[1])

    exit(__load_via_object(status.value, __pos___data__).intvalue);
    return __builtins___none_None;
    #undef status
}

__attr __fn_native__get_argv(__attr __args[])
{
    #define status (__args[1])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef status
}

__attr __fn_native__get_path(__attr __args[])
{
    #define status (__args[1])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef status
}

__attr __fn_native__is(__attr __args[])
{
    #define x (__args[1])
    #define y (__args[2])

    return x.value == y.value ? __builtins___boolean_True : __builtins___boolean_False;
    #undef x
    #undef y
}

__attr __fn_native__is_not(__attr __args[])
{
    #define x (__args[1])
    #define y (__args[2])

    return x.value != y.value ? __builtins___boolean_True : __builtins___boolean_False;
    #undef x
    #undef y
}

__attr __fn_native__int_add(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i + j);
    #undef self
    #undef other
}

__attr __fn_native__int_sub(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i - j);
    #undef self
    #undef other
}

__attr __fn_native__int_mul(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i * j);
    #undef self
    #undef other
}

__attr __fn_native__int_div(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i / j);
    #undef self
    #undef other
}

__attr __fn_native__int_mod(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i % j);
    #undef self
    #undef other
}

__attr __fn_native__int_pow(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int((int) pow(i, j));
    #undef self
    #undef other
}

__attr __fn_native__int_and(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i & j);
    #undef self
    #undef other
}

__attr __fn_native__int_or(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i | j);
    #undef self
    #undef other
}

__attr __fn_native__int_xor(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return the new integer. */
    /* NOTE: No overflow test applied. */
    return __new_int(i ^ j);
    #undef self
    #undef other
}

__attr __fn_native__int_lt(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return a boolean result. */
    return i < j ? __builtins___boolean_True : __builtins___boolean_False;
    #undef self
    #undef other
}

__attr __fn_native__int_gt(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return a boolean result. */
    return i > j ? __builtins___boolean_True : __builtins___boolean_False;
    #undef self
    #undef other
}

__attr __fn_native__int_eq(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return a boolean result. */
    return i == j ? __builtins___boolean_True : __builtins___boolean_False;
    #undef self
    #undef other
}

__attr __fn_native__int_ne(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__ and other.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int j = __load_via_object(other.value, __pos___data__).intvalue;

    /* Return a boolean result. */
    return i != j ? __builtins___boolean_True : __builtins___boolean_False;
    #undef self
    #undef other
}

__attr __fn_native__int_str(__attr __args[])
{
    #define self (__args[1])
    /* self.__data__ interpreted as int */
    int i = __load_via_object(self.value, __pos___data__).intvalue;
    int n = i != 0 ? (int) ceil(log10(i+1)) + 1 : 2;
    char *s = calloc(n, sizeof(char));

    if (i < 0) n++;
    snprintf(s, n, "%d", i);

    /* Return a new string. */
    return __new_str(s);
    #undef self
    #undef other
}

__attr __fn_native__str_add(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__, other.__data__ interpreted as string */
    char *s = __load_via_object(self.value, __pos___data__).strvalue;
    char *o = __load_via_object(other.value, __pos___data__).strvalue;
    int n = strlen(s) + strlen(o) + 1;
    char *r = calloc(n, sizeof(char));

    strncpy(r, s, n);
    strncpy(r + strlen(s), o, n - strlen(s));

    /* Return a new string. */
    return __new_str(r);
    #undef self
    #undef other
}

__attr __fn_native__str_lt(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__, other.__data__ interpreted as string */
    char *s = __load_via_object(self.value, __pos___data__).strvalue;
    char *o = __load_via_object(other.value, __pos___data__).strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) < 0 ? __builtins___boolean_True : __builtins___boolean_False;
    #undef self
    #undef other
}

__attr __fn_native__str_gt(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__, other.__data__ interpreted as string */
    char *s = __load_via_object(self.value, __pos___data__).strvalue;
    char *o = __load_via_object(other.value, __pos___data__).strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) > 0 ? __builtins___boolean_True : __builtins___boolean_False;
    #undef self
    #undef other
}

__attr __fn_native__str_eq(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])
    /* self.__data__, other.__data__ interpreted as string */
    char *s = __load_via_object(self.value, __pos___data__).strvalue;
    char *o = __load_via_object(other.value, __pos___data__).strvalue;

    /* NOTE: Using simple byte-level string operations. */
    return strcmp(s, o) == 0 ? __builtins___boolean_True : __builtins___boolean_False;
    #undef self
    #undef other
}

__attr __fn_native__str_len(__attr __args[])
{
    #define self (__args[1])
    /* self.__data__ interpreted as string */
    char *s = __load_via_object(self.value, __pos___data__).strvalue;

    /* Return the new integer. */
    return __new_int(strlen(s));
    #undef self
}

__attr __fn_native__str_nonempty(__attr __args[])
{
    #define self (__args[1])
    /* self.__data__ interpreted as string */
    char *s = __load_via_object(self.value, __pos___data__).strvalue;

    return strlen(s) ? __builtins___boolean_True : __builtins___boolean_False;
    #undef self
}

__attr __fn_native__list_init(__attr __args[])
{
    #define size (__args[1])
    /* size.__data__ interpreted as fragment */
    __fragment *data = calloc(__load_via_object(size.value, __pos___data__).intvalue, sizeof(__attr));
    __attr attr = {0, .data=data};

    return attr;
    #undef size
}

__attr __fn_native__list_len(__attr __args[])
{
    #define self (__args[1])
    /* self.__data__ interpreted as fragment */
    unsigned int size = __load_via_object(self.value, __pos___data__).data->size;

    /* Return the new integer. */
    return __new_int(size);
    #undef self
}

__attr __fn_native__list_nonempty(__attr __args[])
{
    #define self (__args[1])

    return __load_via_object(self.value, __pos___data__).data->size ? __builtins___boolean_True : __builtins___boolean_False;
    #undef self
}

__attr __fn_native__list_element(__attr __args[])
{
    #define self (__args[1])
    #define index (__args[2])
    /* self.__data__ interpreted as fragment */
    __attr *elements = __load_via_object(self.value, __pos___data__).data->attrs;
    /* index.__data__ interpreted as int */
    int i = __load_via_object(index.value, __pos___data__).intvalue;

    return elements[i];
    #undef self
    #undef index
}

__attr __fn_native__list_to_tuple(__attr __args[])
{
    #define l (__args[1])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef l
}

__attr __fn_native__tuple_init(__attr __args[])
{
    #define size (__args[1])
    /* size.__data__ interpreted as fragment */
    __fragment *data = calloc(__load_via_object(size.value, __pos___data__).intvalue, sizeof(__attr));
    __attr attr = {0, .data=data};

    return attr;
    #undef size
}

__attr __fn_native__tuple_len(__attr __args[])
{
    #define self (__args[1])
    /* self.__data__ interpreted as fragment */
    unsigned int size = __load_via_object(self.value, __pos___data__).data->size;

    /* Return the new integer. */
    return __new_int(size);
    #undef self
}

__attr __fn_native__tuple_element(__attr __args[])
{
    #define self (__args[1])
    #define index (__args[2])
    /* self.__data__ interpreted as fragment */
    __attr *elements = __load_via_object(self.value, __pos___data__).data->attrs;
    /* index.__data__ interpreted as int */
    int i = __load_via_object(index.value, __pos___data__).intvalue;

    return elements[i];
    #undef self
    #undef index
}

__attr __fn_native__isinstance(__attr __args[])
{
    #define obj (__args[1])
    #define cls (__args[2])

    if (__is_instance(obj.value) && __HASATTR(__get_class(obj.value), __TYPEPOS(cls.value), __TYPECODE(cls.value)))
        return __builtins___boolean_True;
    else
        return __builtins___boolean_False;
    #undef obj
    #undef cls
}

__attr __fn_native__read(__attr __args[])
{
    #define fd (__args[1])
    #define n (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef fd
    #undef n
}

__attr __fn_native__write(__attr __args[])
{
    #define fd (__args[1])
    #define str (__args[2])
    /* fd.__data__ interpreted as int */
    int i = __load_via_object(fd.value, __pos___data__).intvalue;
    /* str.__data__ interpreted as string */
    char *s = __load_via_object(str.value, __pos___data__).strvalue;

    write(i, s, sizeof(char) * strlen(s));
    return __builtins___none_None;
    #undef fd
    #undef str
}

/* Module initialisation. */

void __main_native()
{
}

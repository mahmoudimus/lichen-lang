#include <stdlib.h> /* calloc, exit */
#include <unistd.h> /* read, write */
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Native functions. */

__attr __fn_native__exit(__attr __args[])
{
    #define status (__args[1])

    exit(__load_via_object(status.value, __pos___data__).intvalue);
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

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_sub(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_mul(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_div(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_mod(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_pow(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_and(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_or(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_xor(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_rsub(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_rdiv(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_rmod(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_rpow(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_lt(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_gt(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__int_eq(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__str_add(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__str_lt(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__str_gt(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__str_eq(__attr __args[])
{
    #define self (__args[1])
    #define other (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef other
}

__attr __fn_native__str_len(__attr __args[])
{
    #define self (__args[1])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
}

__attr __fn_native__str_nonempty(__attr __args[])
{
    #define self (__args[1])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
}

__attr __fn_native__list_init(__attr __args[])
{
    #define size (__args[1])
    /* size.__data__ interpreted as int */
    __fragment *data = calloc(__load_via_object(size.value, __pos___data__).intvalue, sizeof(__attr));
    __attr attr = {0, .data=data};

    return attr;
    #undef size
}

__attr __fn_native__list_len(__attr __args[])
{
    #define self (__args[1])

    /* NOTE: To be written. */
    return __builtins___none_None;
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

    /* NOTE: To be written. */
    return __builtins___none_None;
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
    /* size.__data__ interpreted as int */
    __fragment *data = calloc(__load_via_object(size.value, __pos___data__).intvalue, sizeof(__attr));
    __attr attr = {0, .data=data};

    return attr;
    #undef size
}

__attr __fn_native__tuple_len(__attr __args[])
{
    #define self (__args[1])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
}

__attr __fn_native__tuple_element(__attr __args[])
{
    #define self (__args[1])
    #define index (__args[2])

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef self
    #undef index
}

__attr __fn_native__isinstance(__attr __args[])
{
    #define obj (__args[1])
    #define cls (__args[2])

    if (__HASATTR(obj.value, __TYPEPOS(cls.value), __TYPECODE(cls.value)))
        return obj;
    else
        return __builtins___none_None;
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

    /* NOTE: To be written. */
    return __builtins___none_None;
    #undef fd
    #undef str
}

/* Module initialisation. */

void __main_native()
{
}

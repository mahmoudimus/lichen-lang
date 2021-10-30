/* Operations depending on program specifics.

Copyright (C) 2015, 2016, 2017, 2018, 2021 Paul Boddie <paul@boddie.org.uk>

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

#include <stdlib.h>
#include "types.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"
#include "exceptions.h"
#include "calls.h"

/* Generic instantiation operations, defining common members. */

void __init(__ref obj, const __table * table, __ref cls)
{
    obj->table = table;
    obj->pos = __INSTANCEPOS;
    __store_via_object(obj, __class__, __ATTRVALUE(cls));
}

__attr __new(const __table * table, __ref cls, size_t size, int immutable)
{
    __ref obj = (__ref) (immutable ? __ALLOCATEIM : __ALLOCATE)(1, size);
    __init(obj, table, cls);
    return __ATTRVALUE(obj);
}

__attr __new_wrapper(__attr context, __attr attr)
{
    return __new___builtins___core_wrapper(__NULL, context, attr);
}

/* Generic internal data allocation. */

__fragment *__new_fragment(__int n) 
{
    /* Allocate space for the list. */

    __fragment *data = (__fragment *) __ALLOCATE(1, __FRAGMENT_SIZE(n));

    /* The initial capacity is the same as the given size. */

    data->size = 0;
    data->capacity = n;
    return data;
}

void __newdata_sequence(__int number, __fragment *data, __attr args[])
{
    __int i;

    /* Copy the given number of values. */

    for (i = 0; i < number; i++)
        data->attrs[i] = args[i];

    data->size = number;
}

__attr __newdata_list(__int number, __attr args[])
{
    __attr self = __NEWINSTANCE(__builtins___list_list);
    __fragment *data = __new_fragment(number);

    /* Store a reference to the data in the object's __data__ attribute. */

    __store_via_object(__VALUE(self), __data__, (__attr) {.seqvalue=data});
    __newdata_sequence(number, data, args);
    return self;
}

__attr __newdata_tuple(__int number, __attr args[])
{
    /* Allocate the tuple and fragment together. */

    __attr self = __new(&__INSTANCETABLE(__builtins___tuple_tuple),
                        &__builtins___tuple_tuple,
                        __INSTANCESIZE(__builtins___tuple_tuple) + __FRAGMENT_SIZE(number), 0);
    __fragment *data = (__fragment *) ((void *) __VALUE(self) + __INSTANCESIZE(__builtins___tuple_tuple));

    /* Store a reference to the data in the object's __data__ attribute. */

    __store_via_object(__VALUE(self), __data__, (__attr) {.seqvalue=data});
    __newdata_sequence(number, data, args);
    return self;
}

#ifdef __HAVE___builtins___dict_dict
__attr __newdata_dict(__int number, __attr args[])
{
    __attr self = __NEWINSTANCE(__builtins___dict_dict);

    /* Create a temporary list using the arguments. */

    __attr tmp = __newdata_list(number, args);

    /* Call __init__ with the dict object and list argument. */

    __fn___builtins___dict_dict___init__(self, tmp);
    return self;
}
#endif /* __HAVE___builtins___dict_dict */

/* Helpers for raising errors within common operations. */

void __raise_eof_error()
{
#ifdef __HAVE___builtins___exception_io_EOFError
    __Raise(__new___builtins___exception_io_EOFError(__NULL));
#endif /* __HAVE___builtins___exception_io_EOFError */
}

void __raise_io_error(__attr value)
{
#ifdef __HAVE___builtins___exception_io_IOError
    __Raise(__new___builtins___exception_io_IOError(__NULL, value));
#endif /* __HAVE___builtins___exception_io_IOError */
}

void __raise_memory_error()
{
    __Raise(__new___builtins___core_MemoryError(__NULL));
}

void __raise_os_error(__attr value, __attr arg)
{
#ifdef __HAVE___builtins___exception_system_OSError
    __Raise(__new___builtins___exception_system_OSError(__NULL, value, arg));
#endif /* __HAVE___builtins___exception_system_OSError */
}

void __raise_overflow_error()
{
    __Raise(__new___builtins___core_OverflowError(__NULL));
}

void __raise_unbound_method_error()
{
    __Raise(__new___builtins___core_UnboundMethodInvocation(__NULL));
}

void __raise_type_error()
{
    __Raise(__new___builtins___core_TypeError(__NULL));
}

void __raise_value_error(__attr value)
{
#ifdef __HAVE___builtins___exception_base_ValueError
    __Raise(__new___builtins___exception_base_ValueError(__NULL, value));
#endif /* __HAVE___builtins___exception_base_ValueError */
}

void __raise_zero_division_error()
{
    __Raise(__new___builtins___core_ZeroDivisionError(__NULL));
}

/* Helper for raising exception instances. */

__attr __ensure_instance(__attr arg)
{
    /* Reserve space for the instance. */

    __attr args[1] = {__NULL};

    /* Return instances as provided. */

    if (__is_instance(__VALUE(arg)))
        return arg;

    /* Invoke non-instances to produce instances. */

    else
        return __invoke(arg, 0, 0, 0, 0, 1, args);
}

/* Generic invocation operations. */

/* Invoke the given callable, supplying keyword argument details in the given
   codes and arguments arrays, indicating the number of arguments described.
   The number of positional arguments is specified, and such arguments then
   follow as conventional function arguments. Typically, at least one argument
   is specified, starting with any context argument.
*/

__attr __invoke(__attr callable, int always_callable,
                unsigned int nkwargs, __param kwcodes[], __attr kwargs[],
                unsigned int nargs, __attr args[])
{
    /* Unwrap any wrapped function. */

    __attr target = __unwrap_callable(callable);

    /* Obtain the __args__ special member, referencing the parameter table. */
    /* Refer to the table and minimum/maximum. */

    const __ptable *ptable = __check_and_load_via_object(__VALUE(target), __args__).ptable;
    const unsigned int min = ptable->min, max = ptable->max;

    /* Reserve enough space for the arguments. */

    __attr *allargs = args, moreargs[max];

    /* Traverse the arguments. */

    unsigned int pos, kwpos;

    /* Check the number of arguments. */

    if ((nargs == max) && (nkwargs == 0))
    {
        /* pass */
    }

    /* NOTE: Should use a more specific exception. */

    else if ((min > (nargs + nkwargs)) || ((nargs + nkwargs) > max))
    {
        __raise_type_error();
    }

    /* Copy the arguments. */

    else if (nargs < max)
    {
        allargs = moreargs;

        for (pos = 0; pos < nargs; pos++)
            allargs[pos] = args[pos];

        /* Erase the remaining arguments. */

        for (pos = nargs; pos < max; pos++)
            __SETNULL(allargs[pos]);

        /* Fill keyword arguments. */

        for (kwpos = 0; kwpos < nkwargs; kwpos++)
        {
            pos = __HASPARAM(ptable, kwcodes[kwpos].pos, kwcodes[kwpos].code);

            /* Check the table entry against the supplied argument details.
               Set the argument but only if it does not overwrite positional
               arguments. */
            /* NOTE: Should use a more specific exception. */

            if ((pos == -1) || (pos < nargs))
                __raise_type_error();

            /* Set the argument using the appropriate position. */

            allargs[pos] = kwargs[kwpos];
        }

        /* Fill the defaults. */

        for (pos = nargs; pos < max; pos++)
        {
            if (__ISNULL(allargs[pos]))
                allargs[pos] = __GETDEFAULT(__VALUE(target), pos - min);
        }
    }

    /* Call with the prepared arguments via a special adaptor function that
       converts the array to an argument list. */

    return __call_with_args(
        always_callable ?
        __get_function_unwrapped(allargs[0], target) :
        __check_and_get_function_unwrapped(allargs[0], target),
        allargs, max);
}

/* Error routines. */

__attr __unbound_method(__attr __self)
{
    __Raise(__new___builtins___core_UnboundMethodInvocation(__NULL));
    return __builtins___none_None; /* superfluous */
}

/* Generic operations depending on specific program details. */

void __SETDEFAULT(__ref obj, int pos, __attr value)
{
    __store_via_object__(obj, __FUNCTION_INSTANCE_SIZE + pos, value);
}

__attr __GETDEFAULT(__ref obj, int pos)
{
    return __load_via_object__(obj, __FUNCTION_INSTANCE_SIZE + pos);
}

int __BOOL(__attr attr)
{
    __ref value;

    /* Non-zero integers yield a non-zero result. Since the integer type can be
       larger than int, a conversion is performed. */

    if (__INTEGER(attr))
        return __TOINT(attr) ? 1 : 0;

    /* Test against True and False explicitly. If necessary, invoke the bool
       function with the object and test against True. */

    value = attr.value;

    return value == &__predefined___builtins___boolean_True ? 1 :
           value == &__predefined___builtins___boolean_False ? 0 :
           __VALUE(__fn___builtins___boolean_bool(__NULL, attr)) == &__predefined___builtins___boolean_True;
}

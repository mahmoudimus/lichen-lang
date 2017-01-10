/* Operations depending on program specifics.

Copyright (C) 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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

/* Generic instantiation operations, defining common members. */

__attr __new(const __table * table, __ref cls, size_t size)
{
    __ref obj = (__ref) __ALLOCATE(1, size);
    __attr self = {obj, obj};
    __attr tmp = {0, cls};
    obj->table = table;
    __store_via_object(obj, __pos___class__, tmp);
    return self;
}

/* Generic internal data allocation. */

__fragment *__new_fragment(unsigned int n) 
{
    /* Allocate space for the list. */

    __fragment *data = (__fragment *) __ALLOCATE(1, __FRAGMENT_SIZE(n));

    /* The initial capacity is the same as the given size. */

    data->size = 0;
    data->capacity = n;
    return data;
}

void __newdata_sequence(__attr args[], unsigned int number)
{
    /* Calculate the size of the fragment. */

    __fragment *data = __new_fragment(number);
    __attr attr = {0, .seqvalue=data};
    unsigned int i, j;

    /* Copy the given number of values, starting from the second element. */

    for (i = 1, j = 0; i <= number; i++, j++)
        data->attrs[j] = args[i];

    data->size = number;

    /* Store a reference to the data in the object's __data__ attribute. */

    __store_via_object(args[0].value, __pos___data__, attr);
}

#ifdef __HAVE___builtins___dict_dict
void __newdata_mapping(__attr args[], unsigned int number)
{
    __attr dict = args[0];
    __attr callargs[2];

    /* Create a temporary list using the arguments. */

    __newliteral___builtins___list_list(args, number);

    /* Call __init__ with the dict object and list argument. */

    callargs[0] = dict;
    callargs[1] = args[0];

    __fn___builtins___dict_dict___init__(callargs);
    args[0] = dict;
}
#endif /* __HAVE___builtins___dict_dict */

/* Helpers for raising errors within common operations. */

void __raise_eof_error()
{
#ifdef __HAVE___builtins___exception_io_EOFError
    __attr args[1];
    __attr exc = __new___builtins___exception_io_EOFError(args);
    __Raise(exc);
#endif /* __HAVE___builtins___exception_io_EOFError */
}

void __raise_incomplete_sequence_error(__attr value, __attr arg)
{
#ifdef __HAVE_posix_iconv_IncompleteSequenceError
    __attr args[3] = {{0, 0}, value, arg};
    __attr exc = __new_posix_iconv_IncompleteSequenceError(args);
    __Raise(exc);
#endif /* __HAVE_posix_iconv_IncompleteSequenceError */
}

void __raise_invalid_sequence_error(__attr value, __attr arg)
{
#ifdef __HAVE_posix_iconv_InvalidSequenceError
    __attr args[3] = {{0, 0}, value, arg};
    __attr exc = __new_posix_iconv_InvalidSequenceError(args);
    __Raise(exc);
#endif /* __HAVE_posix_iconv_InvalidSequenceError */
}

void __raise_io_error(__attr value)
{
#ifdef __HAVE___builtins___exception_io_IOError
    __attr args[2] = {{0, 0}, value};
    __attr exc = __new___builtins___exception_io_IOError(args);
    __Raise(exc);
#endif /* __HAVE___builtins___exception_io_IOError */
}

void __raise_memory_error()
{
    __attr args[1];
    __attr exc = __new___builtins___core_MemoryError(args);
    __Raise(exc);
}

void __raise_os_error(__attr value, __attr arg)
{
#ifdef __HAVE___builtins___exception_system_OSError
    __attr args[3] = {{0, 0}, value, arg};
    __attr exc = __new___builtins___exception_system_OSError(args);
    __Raise(exc);
#endif /* __HAVE___builtins___exception_system_OSError */
}

void __raise_overflow_error()
{
    __attr args[1];
    __attr exc = __new___builtins___core_OverflowError(args);
    __Raise(exc);
}

void __raise_type_error()
{
    __attr args[1];
    __attr exc = __new___builtins___core_TypeError(args);
    __Raise(exc);
}

void __raise_zero_division_error()
{
    __attr args[1];
    __attr exc = __new___builtins___core_ZeroDivisionError(args);
    __Raise(exc);
}

/* Helper for raising exception instances. */

__attr __ensure_instance(__attr arg)
{
    /* Reserve space for the instance. */

    __attr args[1];

    /* Return instances as provided. */

    if (__is_instance(arg.value))
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
    /* Obtain the __args__ special member, referencing the parameter table. */

    __attr minparams = __check_and_load_via_object(callable.value, __pos___args__, __code___args__);

    /* Refer to the table and minimum/maximum. */

    const __ptable *ptable = minparams.ptable;
    const unsigned int min = minparams.min, max = ptable->size;

    /* Reserve enough space for the arguments. */

    __attr allargs[max];

    /* Traverse the arguments. */

    unsigned int pos, kwpos;

    /* Check the number of arguments. */

    if ((min > (nargs + nkwargs)) || ((nargs + nkwargs) > max))
        return __NULL;

    /* Copy the arguments. */

    for (pos = 0; pos < nargs; pos++)
        allargs[pos] = args[pos];

    /* Erase the remaining arguments. */

    for (pos = nargs; pos < max; pos++)
    {
        allargs[pos].value = 0;
    }

    /* Fill keyword arguments. */

    for (kwpos = 0; kwpos < nkwargs; kwpos++)
    {
        pos = __HASPARAM(ptable, kwcodes[kwpos].pos, kwcodes[kwpos].code);

        /* Check the table entry against the supplied argument details.
           Set the argument but only if it does not overwrite positional
           arguments. */

        if ((pos == -1) || (pos < nargs))
            return __NULL;

        /* Set the argument using the appropriate position. */

        allargs[pos] = kwargs[kwpos];
    }

    /* Fill the defaults. */

    for (pos = nargs; pos < max; pos++)
    {
        if (allargs[pos].value == 0)
            allargs[pos] = __GETDEFAULT(callable.value, pos - min);
    }

    /* Call with the prepared arguments. */

    return (always_callable ? __load_via_object(callable.value, __pos___fn__)
                            : __check_and_load_via_object(callable.value, __pos___fn__, __code___fn__)
                            ).fn(allargs);
}

/* Error routines. */

__attr __unbound_method(__attr args[])
{
    __attr excargs[1];
    __attr exc = __new___builtins___core_UnboundMethodInvocation(excargs);
    __Raise(exc);
    return __builtins___none_None; /* superfluous */
}

/* Generic operations depending on specific program details. */

void __SETDEFAULT(__ref obj, int pos, __attr value)
{
    __store_via_object(obj, __FUNCTION_INSTANCE_SIZE + pos, value);
}

__attr __GETDEFAULT(__ref obj, int pos)
{
    return __load_via_object(obj, __FUNCTION_INSTANCE_SIZE + pos);
}

int __BOOL(__attr attr)
{
    __attr args[2] = {{0, 0}, attr};

    /* Invoke the bool function with the object and test against True. */

    return __fn___builtins___boolean_bool(args).value == __builtins___boolean_True.value;
}

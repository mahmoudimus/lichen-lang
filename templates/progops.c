/* Operations depending on program specifics.
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
    __ref obj = (__ref) calloc(1, size);
    __attr self = {obj, obj};
    __attr tmp = {0, cls};
    obj->table = table;
    __store_via_object(obj, __pos___class__, tmp);
    return self;
}

/* Generic internal data allocation. */

__attr __newdata(__attr args[], unsigned int number)
{
    /* Calculate the size of the fragment. */

    __fragment *data = (__fragment *) calloc(1, __FRAGMENT_SIZE(number));
    __attr attr = {0, .data=data};
    unsigned int i, j;

    /* Copy the given number of values, starting from the second element. */

    for (i = 1, j = 0; i <= number; i++, j++)
        data->attrs[j] = args[i];

    data->size = number;
    data->capacity = number;
    return attr;
}

/* A helper for raising type errors within common operations. */

void __raise_type_error()
{
    __attr args[1];
    __attr exc = __TYPE_ERROR_INSTANTIATOR(args);
    __Raise(exc);
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

    __attr minparams = __load_via_object(callable.value, __pos___args__);

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
            allargs[pos] = __GETDEFAULT(callable.value, pos - nargs);
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

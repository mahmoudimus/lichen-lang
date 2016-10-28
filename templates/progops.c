/* Operations depending on program specifics.
*/

#include <stdlib.h>
#include "types.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include <stdio.h>

/* Generic instantiation operations, defining common members. */

__attr __new(const __table * table, __ref cls, int size)
{
    __ref obj = calloc(1, size);
    __attr self = {obj, obj};
    __attr tmp = {0, cls};
    obj->table = table;
    __store_via_object(obj, __pos___class__, tmp);
    return self;
}

/* Generic invocation operations. */

/* Invoke the given callable, supplying keyword argument details in the given
   codes and arguments arrays, indicating the number of arguments described.
   The number of positional arguments is specified, and such arguments then
   follow as conventional function arguments. Typically, at least one argument
   is specified, starting with any context argument.
*/

__attr __invoke(__attr callable,
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
        return null;

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
            return null;

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

    return __load_via_object(callable.value, __pos___fn__).fn(allargs);
}

/* Error routines. */

__attr __unbound_method(__attr args[])
{
    /* NOTE: Should raise an exception. */

    fprintf(stderr, "Unbound method called!\n");
    exit(1);
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
    return attr.value == __builtins___bool_True.value;
}

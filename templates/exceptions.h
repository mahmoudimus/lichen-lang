#ifndef __EXCEPTIONS_H__
#define __EXCEPTIONS_H__

#include "cexcept.h"
#include "types.h"

/* Define the exception type. */

typedef struct
{
    __attr arg;
    int raising;
    int raising_else;
    int completing;
} __exc;

define_exception_type(__exc);
#undef define_exception_type

extern struct __exception_context __the_exception_context[1];

/* More specific macros. */

#define __Raise(value) __Throw ((__exc) {value, 1, 0, 0})
#define __RaiseElse(value) __Throw ((__exc) {value, 0, 1, 0})
#define __Return(value) __Throw ((__exc) {value, 0, 0, 1})
#define __Complete __Throw((__exc) {__NULL, 0, 0, 1})

#endif /* __EXCEPTIONS_H__ */

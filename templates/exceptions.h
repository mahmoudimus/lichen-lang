/* Exception definitions.

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

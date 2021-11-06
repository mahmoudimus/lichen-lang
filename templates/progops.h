/* Operations depending on program specifics.

Copyright (C) 2015-2019, 2021 Paul Boddie <paul@boddie.org.uk>

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

#ifndef __PROGOPS_H__
#define __PROGOPS_H__

#include <stdlib.h> /* size_t */
#include "types.h"
#include "main.h"

/* Generic instantiation operations, defining common members. */

__attr __new(const __table *table, __ref cls, size_t size, int immutable);
__attr __new_wrapper(__attr context, __attr attr);

/* Generic internal data allocation. */

__fragment *__new_fragment(__int n);

__attr __newdata_list(__int number, __attr args[]);
__attr __newdata_tuple(__int number, __attr args[]);

#define __newliteral___builtins___list_list(NUM, ...) __newdata_list(NUM, __ARGS(__VA_ARGS__))
#define __newliteral___builtins___tuple_tuple(NUM, ...) __newdata_tuple(NUM, __ARGS(__VA_ARGS__))

/* Potentially superfluous operations. */

#ifdef __HAVE___builtins___dict_dict
__attr __newdata_dict(__int number, __attr args[]);
#define __newliteral___builtins___dict_dict(NUM, ...) __newdata_dict(NUM, __ARGS(__VA_ARGS__))
#endif

/* Helpers for raising errors within common operations. */

void __raise_eof_error();
void __raise_floating_point_error();
void __raise_io_error(__attr value);
void __raise_memory_error();
void __raise_os_error(__attr value, __attr arg);
void __raise_overflow_error();
void __raise_unbound_method_error();
void __raise_underflow_error();
void __raise_value_error(__attr value);
void __raise_zero_division_error();
void __raise_type_error();

/* Helper for raising exception instances. */

__attr __ensure_instance(__attr arg);

/* Generic invocation operations. */

__attr __invoke(__attr callable, int always_callable,
                   unsigned int nkwargs, __param kwcodes[], __attr kwargs[],
                   unsigned int nargs, __attr args[]);

/* Error routines. */

__attr __unbound_method(__attr __self);

/* Generic operations depending on specific program details. */

void __SETDEFAULT(__ref obj, int pos, __attr value);
__attr __GETDEFAULT(__ref obj, int pos);
int __BOOL(__attr attr);

/* Convenience definitions. */

#define __OBJTYPE(CLS) __obj_##CLS
#define __INSTANCESIZE(CLS) sizeof(__OBJTYPE(CLS))
#define __INSTANCETABLE(CLS) (__InstanceTable_##CLS)
#define __NEWINSTANCE(CLS) __new(&__INSTANCETABLE(CLS), &CLS, __INSTANCESIZE(CLS), 0)
#define __NEWINSTANCEIM(CLS) __new(&__INSTANCETABLE(CLS), &CLS, __INSTANCESIZE(CLS), 1)
#define __ISINSTANCE(ATTR, TYPE) __BOOL(__fn_native_introspection_isinstance(__NULL, ATTR, TYPE))

/* Operations for accessing trailing data. */

#define __get_trailing_data(ATTR, TYPE) (((__OBJTYPE(TYPE) *) (__VALUE(ATTR)))->trailing)
#define __set_trailing_data(ATTR, TYPE, VALUE) ((__OBJTYPE(TYPE) *) (__VALUE(ATTR)))->trailing = VALUE;

/* Specialised trailing data functions. */

__int __TOINT(__attr attr);

/* Instance test functions, to be replaced by tagged pointer usage. */

int __INTEGER(__attr attr);
int __FLOAT(__attr attr);

#endif /* __PROGOPS_H__ */

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

#ifndef __PROGOPS_H__
#define __PROGOPS_H__

#include <stdlib.h>
#include "types.h"

/* Generic instantiation operations, defining common members. */

__attr __new(const __table *table, __ref cls, size_t size);

/* Generic internal data allocation. */

__fragment *__new_fragment(unsigned int n);

void __newdata_sequence(__attr args[], unsigned int number);

#ifdef __HAVE___builtins___dict_dict
void __newdata_mapping(__attr args[], unsigned int number);
#endif /* __HAVE___builtins___dict_dict */

/* Helpers for raising errors within common operations. */

void __raise_eof_error();

void __raise_io_error(__attr value);

void __raise_memory_error();

void __raise_os_error(__attr value, __attr arg);

void __raise_overflow_error();

void __raise_zero_division_error();

void __raise_type_error();

/* Helper for raising exception instances. */

__attr __ensure_instance(__attr arg);

/* Generic invocation operations. */

__attr __invoke(__attr callable, int always_callable,
                unsigned int nkwargs, __param kwcodes[], __attr kwargs[],
                unsigned int nargs, __attr args[]);

/* Error routines. */

__attr __unbound_method(__attr args[]);

/* Generic operations depending on specific program details. */

void __SETDEFAULT(__ref obj, int pos, __attr value);

__attr __GETDEFAULT(__ref obj, int pos);

int __BOOL(__attr attr);

/* Convenience definitions. */

#define __ISINSTANCE(__ATTR, __TYPE) __BOOL(__fn_native_introspection_isinstance((__attr[]) {{0, 0}, __ATTR, __TYPE}))

#endif /* __PROGOPS_H__ */

/* Native functions for introspection.

Copyright (C) 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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

#ifndef __NATIVE_INTROSPECTION_H__
#define __NATIVE_INTROSPECTION_H__

#include "types.h"

/* Introspection. */

__attr __fn_native_introspection_object_getattr(__attr __self, __attr obj, __attr name, __attr _default);
__attr __fn_native_introspection_isinstance(__attr __self, __attr obj, __attr cls);
__attr __fn_native_introspection_issubclass(__attr __self, __attr obj, __attr cls);

/* Module initialisation. */

void __main_native_introspection();

#endif /* __NATIVE_INTROSPECTION_H__ */

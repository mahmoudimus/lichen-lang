/* Native functions for integer operations.

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

#ifndef __NATIVE_INT_H__
#define __NATIVE_INT_H__

#include "types.h"

/* Integer operations. */

__attr __fn_native_int_is_int(__attr __self, __attr obj);
__attr __fn_native_int_int_add(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_sub(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_mul(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_div(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_mod(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_neg(__attr __self, __attr _data);
__attr __fn_native_int_int_pow(__attr __self, __attr _data, __attr other);

__attr __fn_native_int_int_and(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_not(__attr __self, __attr _data);
__attr __fn_native_int_int_or(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_xor(__attr __self, __attr _data, __attr other);

__attr __fn_native_int_int_lshift(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_rshift(__attr __self, __attr _data, __attr other);

__attr __fn_native_int_int_eq(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_ge(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_gt(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_le(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_lt(__attr __self, __attr _data, __attr other);
__attr __fn_native_int_int_ne(__attr __self, __attr _data, __attr other);

__attr __fn_native_int_int_str(__attr __self, __attr _data);

/* Module initialisation. */

void __main_native_int();

#endif /* __NATIVE_INT_H__ */

/* Native functions for floating point operations.

Copyright (C) 2018 Paul Boddie <paul@boddie.org.uk>

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

#ifndef __NATIVE_FLOAT_H__
#define __NATIVE_FLOAT_H__

#include "types.h"

/* Floating point operations. */

__attr __fn_native_float_float_add(__attr __self, __attr self, __attr other);
__attr __fn_native_float_float_sub(__attr __self, __attr self, __attr other);
__attr __fn_native_float_float_mul(__attr __self, __attr self, __attr other);
__attr __fn_native_float_float_div(__attr __self, __attr self, __attr other);
__attr __fn_native_float_float_mod(__attr __self, __attr self, __attr other);
__attr __fn_native_float_float_neg(__attr __self, __attr self);
__attr __fn_native_float_float_pow(__attr __self, __attr self, __attr other);

__attr __fn_native_float_float_le(__attr __self, __attr self, __attr other);
__attr __fn_native_float_float_lt(__attr __self, __attr self, __attr other);
__attr __fn_native_float_float_ge(__attr __self, __attr self, __attr other);
__attr __fn_native_float_float_gt(__attr __self, __attr self, __attr other);
__attr __fn_native_float_float_eq(__attr __self, __attr self, __attr other);
__attr __fn_native_float_float_ne(__attr __self, __attr self, __attr other);

__attr __fn_native_float_float_str(__attr __self, __attr self);
__attr __fn_native_float_float_int(__attr __self, __attr self);

/* Module initialisation. */

void __main_native_float();

#endif /* __NATIVE_FLOAT_H__ */

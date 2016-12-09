/* Native functions for integer operations.

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

#ifndef __NATIVE_INT_H__
#define __NATIVE_INT_H__

#include "types.h"

/* Integer operations. */

__attr __fn_native_int_int_add(__attr __args[]);
__attr __fn_native_int_int_div(__attr __args[]);
__attr __fn_native_int_int_mod(__attr __args[]);
__attr __fn_native_int_int_mul(__attr __args[]);
__attr __fn_native_int_int_neg(__attr __args[]);
__attr __fn_native_int_int_pow(__attr __args[]);
__attr __fn_native_int_int_sub(__attr __args[]);

__attr __fn_native_int_int_and(__attr __args[]);
__attr __fn_native_int_int_not(__attr __args[]);
__attr __fn_native_int_int_or(__attr __args[]);
__attr __fn_native_int_int_xor(__attr __args[]);

__attr __fn_native_int_int_rdiv(__attr __args[]);
__attr __fn_native_int_int_rmod(__attr __args[]);
__attr __fn_native_int_int_rpow(__attr __args[]);
__attr __fn_native_int_int_rsub(__attr __args[]);

__attr __fn_native_int_int_lt(__attr __args[]);
__attr __fn_native_int_int_gt(__attr __args[]);
__attr __fn_native_int_int_eq(__attr __args[]);
__attr __fn_native_int_int_ne(__attr __args[]);

__attr __fn_native_int_int_str(__attr __args[]);

/* Module initialisation. */

void __main_native_int();

#endif /* __NATIVE_INT_H__ */

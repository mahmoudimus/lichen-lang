/* Native functions for string operations.

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

#ifndef __NATIVE_STR_H__
#define __NATIVE_STR_H__

/* String operations. */

__attr __fn_native_str_str_add(__attr __args[]);
__attr __fn_native_str_str_lt(__attr __args[]);
__attr __fn_native_str_str_gt(__attr __args[]);
__attr __fn_native_str_str_eq(__attr __args[]);
__attr __fn_native_str_str_len(__attr __args[]);
__attr __fn_native_str_str_nonempty(__attr __args[]);
__attr __fn_native_str_str_ord(__attr __args[]);
__attr __fn_native_str_str_substr(__attr __args[]);

/* Module initialisation. */

void __main_native_str();

#endif /* __NATIVE_STR_H__ */

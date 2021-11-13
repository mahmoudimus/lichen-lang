/* Native functions for list operations.

Copyright (C) 2016, 2017, 2021 Paul Boddie <paul@boddie.org.uk>

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

#ifndef __NATIVE_LIST_H__
#define __NATIVE_LIST_H__

#include "types.h"

/* List operations. */

__attr __fn_native_list_list_init(__attr __self, __attr size);
__attr __fn_native_list_list_setsize(__attr __self, __attr _data, __attr size);
__attr __fn_native_list_list_append(__attr __self, __attr self, __attr value);
__attr __fn_native_list_list_concat(__attr __self, __attr self, __attr other);
__attr __fn_native_list_list_len(__attr __self, __attr _data);
__attr __fn_native_list_list_nonempty(__attr __self, __attr _data);
__attr __fn_native_list_list_element(__attr __self, __attr _data, __attr index);
__attr __fn_native_list_list_setelement(__attr __self, __attr _data, __attr index, __attr value);

/* Module initialisation. */

void __main_native_list();

#endif /* __NATIVE_LIST_H__ */

/* Common operations for native functions.

Copyright (C) 2016, 2017, 2018 Paul Boddie <paul@boddie.org.uk>

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

#ifndef __NATIVE_COMMON_H__
#define __NATIVE_COMMON_H__

#include "types.h"

/* Utility macro for the special integer representation. */

#define __new_int(VALUE) __INTVALUE(VALUE)

/* Utility functions. */

__attr __new_str(char *s, int size);
__attr __new_list(__fragment *f);
__attr __new_float(double n);
__fragment *__fragment_append(__fragment *data, __attr value);

#endif /* __NATIVE_COMMON_H__ */

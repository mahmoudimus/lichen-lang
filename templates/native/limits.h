/* Native functions for limit definition.

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

#ifndef __NATIVE_LIMITS_H__
#define __NATIVE_LIMITS_H__

#include "types.h"

/* Limit definition. */

__attr __fn_native_limits_get_maxint(__attr __self);
__attr __fn_native_limits_get_minint(__attr __self);

/* Module initialisation. */

void __main_native_limits();

#endif /* __NATIVE_LIMITS_H__ */

/* Native functions for Unicode operations.

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

#ifndef __NATIVE_UNICODE_H__
#define __NATIVE_UNICODE_H__

/* Unicode operations. */

__attr __fn_native_unicode_unicode_len(__attr __self, __attr _data, __attr _size);
__attr __fn_native_unicode_unicode_ord(__attr __self, __attr _data, __attr _size);
__attr __fn_native_unicode_unicode_substr(__attr __self, __attr _data, __attr _size, __attr start, __attr end, __attr step);
__attr __fn_native_unicode_unicode_unichr(__attr __self, __attr value);

/* Module initialisation. */

void __main_native_unicode();

#endif /* __NATIVE_UNICODE_H__ */

/* Signal handling.

Copyright (C) 2019 Paul Boddie <paul@boddie.org.uk>

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

#ifndef __SIGNALS_H__
#define __SIGNALS_H__

#include <signal.h>

void __signals_install_handlers();
void __signals_fpe_handler(int signum, siginfo_t *siginfo, void *context);

#endif /* __SIGNALS_H__ */

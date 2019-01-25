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

#include <setjmp.h>
#include <signal.h>
#include <stdlib.h>

#include "signals.h"

void __signals_install_handlers()
{
    struct sigaction context;

    context.sa_flags = SA_SIGINFO;
    context.sa_sigaction = __signals_fpe_handler;
    sigemptyset(&context.sa_mask);

    /* NOTE: Should test for -1 and errno. */

    sigaction(SIGFPE, &context, NULL);
}

jmp_buf __fpe_env;

void __signals_fpe_handler(int signum, siginfo_t *siginfo, void *context)
{
    /* Return from setjmp with the signal number. */

    longjmp(__fpe_env, siginfo->si_code);
}

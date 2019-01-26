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

#include <signal.h>
#include <stdlib.h>

#include "signals.h"
#include "progops.h"

void __signals_install_handlers()
{
    struct sigaction context;

    context.sa_flags = SA_SIGINFO;
    context.sa_sigaction = __signals_fpe_handler;
    sigemptyset(&context.sa_mask);

    /* NOTE: Should test for -1 and errno. */

    sigaction(SIGFPE, &context, NULL);
}

void __signals_fpe_handler(int signum, siginfo_t *siginfo, void *context)
{
    /* Return from setjmp using the signal number. */

    switch (siginfo->si_code)
    {
        case FPE_FLTOVF:
        __raise_overflow_error();
        break;

        case FPE_FLTUND:
        __raise_underflow_error();
        break;

        case FPE_FLTDIV:
        __raise_zero_division_error();
        break;

        default:
        __raise_floating_point_error();
        break;
    }
}

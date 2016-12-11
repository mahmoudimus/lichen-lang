/* Native functions for character set conversion.

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

#include <iconv.h> /* iconv, iconv_close, iconv_open */
#include <string.h> /* memcpy */
#include <errno.h> /* errno */
#include "native/common.h"
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

static const size_t OUTBUFSIZE_MIN = 16;

/* Character set conversion. */

__attr __fn_native_iconv_iconv(__attr __args[])
{
    __attr * const cd = &__args[1];
    __attr * const instr = &__args[2];
    __attr * const state = &__args[3];
    /* cd interpreted as iconv_t */
    iconv_t c = (iconv_t) cd->datavalue;
    /* instr.__data__ interpreted as string */
    char *inbuf = __load_via_object(instr->value, __pos___data__).strvalue;
    /* state.__data__ interpreted as list */
    __fragment *f = __load_via_object(state->value, __pos___data__).seqvalue;

    /* Obtain the start position from the state. */

    int start = __load_via_object(f->attrs[0].value, __pos___data__).intvalue;
    int remaining = __load_via_object(f->attrs[1].value, __pos___data__).intvalue;

    /* Allocate a string for the output buffer using the remaining input size
       as a guide. */

    size_t outbufsize = remaining < OUTBUFSIZE_MIN ? OUTBUFSIZE_MIN : remaining;
    size_t outbytesleft = outbufsize;
    size_t inbytesleft = remaining;

    char buf[outbytesleft];
    char *outbuf = buf, *outbufstart = outbuf, *resultbuf;
    size_t result, outbytestotal;

    /* Convert from the start point. */

    inbuf += start;

    errno = 0;
    result = iconv(c, &inbuf, &inbytesleft, &outbuf, &outbytesleft);

    /* Return any string. */

    if ((result != -1) || (errno == E2BIG))
    {
        outbytestotal = outbufsize - outbytesleft;
        resultbuf = __ALLOCATE(outbytestotal + 1, sizeof(char));
        memcpy(resultbuf, outbufstart, outbytestotal);

        /* Mutate the state to indicate the next input buffer position. */

        f->attrs[0] = __new_int(start + remaining - inbytesleft);
        f->attrs[1] = __new_int(inbytesleft);
        return __new_str(resultbuf, outbytestotal);
    }

    /* Invalid sequence. */

    if (errno == EILSEQ)
    {
        resultbuf = __ALLOCATE(inbytesleft + 1, sizeof(char));
        memcpy(resultbuf, inbuf, inbytesleft);
        __raise_os_error(__new_int(errno), __new_str(resultbuf, inbytesleft));
    }

    /* Incomplete sequence. */

    else if (errno == EINVAL)
    {
        resultbuf = __ALLOCATE(inbytesleft + 1, sizeof(char));
        memcpy(resultbuf, inbuf, inbytesleft);
        __raise_os_error(__new_int(errno), __new_str(resultbuf, inbytesleft));
    }

    /* General failure. */

    else
        __raise_os_error(__new_int(errno), __builtins___none_None);
}

__attr __fn_native_iconv_iconv_close(__attr __args[])
{
    __attr * const cd = &__args[1];
    /* cd interpreted as iconv_t */
    iconv_t c = (iconv_t) cd->datavalue;

    errno = 0;

    if (iconv_close(c) == -1)
        __raise_os_error(__new_int(errno), __builtins___none_None);

    return __builtins___none_None;
}

__attr __fn_native_iconv_iconv_open(__attr __args[])
{
    __attr * const tocode = &__args[1];
    __attr * const fromcode = &__args[2];
    /* tocode.__data__ interpreted as string */
    char *t = __load_via_object(tocode->value, __pos___data__).strvalue;
    /* fromcode.__data__ interpreted as string */
    char *f = __load_via_object(fromcode->value, __pos___data__).strvalue;
    iconv_t result;
    __attr attr;

    errno = 0;
    result = iconv_open(t, f);

    if (result == (iconv_t) -1)
        __raise_os_error(__new_int(errno), __builtins___none_None);

    /* Return the descriptor as an opaque value. */

    attr.context = 0;
    attr.datavalue = (void *) result;
    return attr;
}

/* Module initialisation. */

void __main_native_iconv()
{
}

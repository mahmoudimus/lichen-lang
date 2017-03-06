/* Native functions for input/output.

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

#include <unistd.h> /* read, write */
#include <string.h> /* strcmp, memcpy */
#include <stdio.h>  /* fdopen, snprintf */
#include <errno.h>  /* errno */
#include "native/common.h"
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

/* Input/output. */

__attr __fn_native_io_fclose(__attr __self, __attr fp)
{
    /* fp interpreted as FILE reference */
    FILE *f = (FILE *) fp.datavalue;

    errno = 0;
    if (fclose(f))
        __raise_io_error(__new_int(errno));

    return __builtins___none_None;
}

__attr __fn_native_io_fflush(__attr __self, __attr fp)
{
    /* fp interpreted as FILE reference */
    FILE *f = (FILE *) fp.datavalue;

    errno = 0;
    if (fflush(f))
        __raise_io_error(__new_int(errno));

    return __builtins___none_None;
}

__attr __fn_native_io_fopen(__attr __self, __attr filename, __attr mode)
{
    /* filename interpreted as string */
    char *fn = __load_via_object(filename.value, __data__).strvalue;
    /* mode interpreted as string */
    char *s = __load_via_object(mode.value, __data__).strvalue;
    FILE *f;
    __attr attr;

    errno = 0;
    f = fopen(fn, s);

    /* Produce an exception if the operation failed. */

    if (f == NULL)
        __raise_io_error(__new_int(errno));

    /* Return the __data__ attribute. */

    else
    {
        attr.datavalue = (void *) f;
        return attr;
    }

    /* Should never be reached: included to satisfy the compiler. */

    return __builtins___none_None;
}

__attr __fn_native_io_fdopen(__attr __self, __attr fd, __attr mode)
{
    /* fd interpreted as int */
    int i = __load_via_object(fd.value, __data__).intvalue;
    /* mode interpreted as string */
    char *s = __load_via_object(mode.value, __data__).strvalue;
    FILE *f;
    __attr attr;

    errno = 0;
    f = fdopen(i, s);

    /* Produce an exception if the operation failed. */

    if (f == NULL)
        __raise_io_error(__new_int(errno));

    /* Return the __data__ attribute. */

    else
    {
        attr.datavalue = (void *) f;
        return attr;
    }

    /* Should never be reached: included to satisfy the compiler. */

    return __builtins___none_None;
}

__attr __fn_native_io_fread(__attr __self, __attr fp, __attr size)
{
    /* fp interpreted as FILE reference */
    FILE *f = (FILE *) fp.datavalue;
    /* size interpreted as int */
    int to_read = __load_via_object(size.value, __data__).intvalue;
    char buf[to_read];
    size_t have_read;
    int error;
    char *s;

    have_read = fread(buf, sizeof(char), to_read, f);

    if (have_read != to_read)
    {
        if (feof(f) && (have_read == 0))
            __raise_eof_error();
        else if ((error = ferror(f)))
            __raise_io_error(__new_int(error));
    }

    /* Reserve space for a new string. */

    s = __ALLOCATE(have_read + 1, sizeof(char));
    memcpy(s, (char *) buf, have_read); /* does not null terminate but final byte should be zero */
    return __new_str(s, have_read);
}

__attr __fn_native_io_fwrite(__attr __self, __attr fp, __attr str)
{
    /* fp interpreted as FILE reference */
    FILE *f = (FILE *) fp.datavalue;
    /* str interpreted as string */
    char *s = __load_via_object(str.value, __data__).strvalue;
    int to_write = __load_via_object(str->value, __size__).intvalue;
    size_t have_written = fwrite(s, sizeof(char), to_write, f);
    int error;

    if (have_written != to_write)
    {
        if (feof(f))
            __raise_eof_error();
        else if ((error = ferror(f)))
            __raise_io_error(__new_int(error));
    }

    return __builtins___none_None;
}

__attr __fn_native_io_close(__attr __self, __attr fd)
{
    /* fd interpreted as int */
    int i = __load_via_object(fd.value, __data__).intvalue;

    errno = 0;
    if (close(i) == -1)
        __raise_io_error(__new_int(errno));

    return __builtins___none_None;
}

__attr __fn_native_io_read(__attr __self, __attr fd, __attr n)
{
    /* fd interpreted as int */
    int i = __load_via_object(fd.value, __data__).intvalue;
    /* n interpreted as int */
    int to_read = __load_via_object(n.value, __data__).intvalue;
    char buf[to_read];
    ssize_t have_read;
    char *s;

    errno = 0;
    have_read = read(i, buf, to_read * sizeof(char));

    if (have_read == -1)
        __raise_io_error(__new_int(errno));

    /* Reserve space for a new string. */

    s = __ALLOCATE(have_read + 1, 1);
    memcpy(s, (char *) buf, have_read); /* does not null terminate but final byte should be zero */
    return __new_str(s, have_read);
}

__attr __fn_native_io_write(__attr __self, __attr fd, __attr str)
{
    /* fd interpreted as int */
    int i = __load_via_object(fd.value, __data__).intvalue;
    /* str interpreted as string */
    char *s = __load_via_object(str.value, __data__).strvalue;
    int size = __load_via_object(str.value, __size__).intvalue;
    ssize_t have_written;

    errno = 0;
    have_written = write(i, s, sizeof(char) * size);

    if (have_written == -1)
        __raise_io_error(__new_int(errno));

    return __new_int(have_written);
}

/* Module initialisation. */

void __main_native_io()
{
}

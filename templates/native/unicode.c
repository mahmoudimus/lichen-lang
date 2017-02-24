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

#include "native/common.h"
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"

static inline int boundary(char c)
{
    return ((c & 0xc0) == 0xc0) || !(c & 0x80);
}

static inline int boundary_value(char c)
{
    if (!(c & 0x80)) return c;
    else if ((c & 0xf8) == 0xf0) return c & 0x07;
    else if ((c & 0xf0) == 0xe0) return c & 0x0f;
    else if ((c & 0xe0) == 0xc0) return c & 0x1f;
    else return 0;
}

static unsigned int nextpos(char *s, unsigned int size, unsigned int bytestart)
{
    unsigned int i = bytestart;

    while (i < size)
    {
        i++;
        if (boundary(s[i]))
            break;
    }

    return i;
}

static unsigned int prevpos(char *s, unsigned int bytestart)
{
    unsigned int i = bytestart;

    while (i > 0)
    {
        i--;
        if (boundary(s[i]))
            break;
    }

    return i;
}

/* Unicode operations. */

__attr __fn_native_unicode_unicode_len(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const _size = &__args[2];
    /* _data interpreted as string */
    char *s = _data->strvalue;
    /* _size interpreted as int */
    int size = _size->intvalue;
    unsigned int i, c = 0;

    for (i = 0; i < size; i++)
        if (boundary(s[i]))
            c++;

    /* Return the new integer. */
    return __new_int(c);
}

__attr __fn_native_unicode_unicode_ord(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const _size = &__args[2];
    /* _data interpreted as string */
    char *s = _data->strvalue;
    /* _size interpreted as int */
    int size = _size->intvalue;
    unsigned int i, c = 0, v;

    for (i = 0; i < size; i++)
    {
        /* Evaluate the current character as a boundary. */

        v = boundary_value(s[i]);

        /* Boundary with characters read: stop reading. */

        if (v && i)
            break;

        /* Boundary: initialise with the extracted value. */

        else if (v)
            c = v;

        /* Not a boundary: shift and combine with the continuation value. */

        else
            c = (c << 6) | (s[i] & 0x3f);
    }

    /* Return the new integer. */
    return __new_int(c);
}

__attr __fn_native_unicode_unicode_substr(__attr __args[])
{
    __attr * const _data = &__args[1];
    __attr * const _size = &__args[2];
    __attr * const start = &__args[3];
    __attr * const end = &__args[4];
    __attr * const step = &__args[5];
    /* _data interpreted as string */
    char *s = _data->strvalue, *sub;
    /* _size interpreted as int */
    int ss = _size->intvalue;
    /* start.__data__ interpreted as int */
    int istart = __load_via_object(start->value, __pos___data__).intvalue;
    /* end.__data__ interpreted as int */
    int iend = __load_via_object(end->value, __pos___data__).intvalue;
    /* step.__data__ interpreted as int */
    int istep = __load_via_object(step->value, __pos___data__).intvalue;

    /* Calculate the number of characters. */
    size_t nchar = ((iend - istart - (istep > 0 ? 1 : -1)) / istep) + 1;
    unsigned int indexes[nchar];

    unsigned int c, d, i, to, from, lastbyte = 0;
    int resultsize = 0;

    /* Find the indexes of the characters. */
    if (istep > 0)
    {
        /* Get the first byte position. */
        for (c = 0; c < istart; c++)
            lastbyte = nextpos(s, ss, lastbyte);

        /* Get each subsequent byte position. */
        for (c = istart, i = 0; i < nchar; c += istep, i++)
        {
            indexes[i] = lastbyte;

            /* Add the character size to the result size. */
            resultsize += nextpos(s, ss, lastbyte) - lastbyte;

            for (d = c; d < c + istep; d++)
                lastbyte = nextpos(s, ss, lastbyte);
        }
    }
    else
    {
        /* Get the first byte position. */
        for (c = 0; c < istart; c++)
            lastbyte = nextpos(s, ss, lastbyte);

        /* Get each subsequent byte position. */
        for (c = istart, i = 0; i < nchar; c += istep, i++)
        {
            indexes[i] = lastbyte;

            /* Add the character size to the result size. */
            resultsize += nextpos(s, ss, lastbyte) - lastbyte;

            for (d = c; d > c + istep; d--)
                lastbyte = prevpos(s, lastbyte);
        }
    }

    /* Reserve space for a new string. */
    sub = (char *) __ALLOCATE(resultsize + 1, sizeof(char));

    /* Does not null terminate but final byte should be zero. */
    for (i = 0, to = 0; i < nchar; i++)
    {
        from = indexes[i];
        do
        {
            sub[to++] = s[from++];
        } while (!boundary(s[from]));
    }

    return __new_str(sub, resultsize);
}

__attr __fn_native_unicode_unicode_unichr(__attr __args[])
{
    __attr * const value = &__args[1];
    /* value interpreted as int */
    int i = value->intvalue;
    unsigned int resultsize;
    char *s;

    if (i < 128) resultsize = 1;
    else if (i < 2048) resultsize = 2;
    else if (i < 65536) resultsize = 3;
    else resultsize = 4;

    /* Reserve space for a new string. */

    s = (char *) __ALLOCATE(resultsize + 1, sizeof(char));

    /* Populate the string. */

    if (i < 128) s[0] = (char) i;
    else if (i < 2048)
    {
        s[0] = 0b11000000 | (i >> 6);
        s[1] = 0b10000000 | (i & 0b00111111);
    }
    else if (i < 65536)
    {
        s[0] = 0b11100000 | (i >> 12);
        s[1] = 0b10000000 | ((i >> 6) & 0b00111111);
        s[2] = 0b10000000 | (i & 0b00111111);
    }
    else
    {
        s[0] = 0b11110000 | (i >> 18);
        s[1] = 0b10000000 | ((i >> 12) & 0b00111111);
        s[2] = 0b10000000 | ((i >> 6) & 0b00111111);
        s[3] = 0b10000000 | (i & 0b00111111);
    }

    return __new_str(s, resultsize);
}

/* Module initialisation. */

void __main_native_unicode()
{
}

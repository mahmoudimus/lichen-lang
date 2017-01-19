/* Runtime types.

Copyright (C) 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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

#ifndef __TYPES_H__
#define __TYPES_H__

#include <stddef.h> /* size_t */

/* Attribute tables are lists of codes confirming the presence of attributes. */

typedef struct __table
{
    const unsigned int size, attrs[];
} __table;

/* Parameter tables are lists of codes confirming the presence of parameters, as
   well as the positions of those parameters in the list for a given function.
*/

typedef struct __param
{
    unsigned short code, pos;
} __param;

typedef struct __ptable
{
    const unsigned int size;
    const __param params[];
} __ptable;

/* Attributes are context and value pairs.
   Objects are collections of attributes.
   Object references are references to tables and collections of attributes.
   Attribute references are references to single attributes. */

typedef struct __obj __obj;
typedef struct __fragment __fragment;

typedef struct __attr
{
    /* One of... */
    union
    {
        __obj * context;        /* attribute context */
        __obj * b;              /* bound callable object */
        unsigned int min;       /* minimum number of parameters */
        unsigned int code;      /* parameter table code for key */

        size_t size;            /* size of value */
    };

    /* One of... */
    union
    {
        __obj * value;          /* attribute value */
        const __ptable * ptable;/* parameter table */
        unsigned int pos;       /* parameter table position for key */
        struct __attr (*fn)();  /* callable details */

        int intvalue;           /* integer value */
        double floatvalue;      /* floating point value */
        char * strvalue;        /* string value */
        __fragment * seqvalue;  /* sequence data */
        void * datavalue;       /* object-specific data */
    };
} __attr;

typedef struct __obj
{
    const __table * table;      /* attribute table */
    unsigned int pos;           /* position of attribute indicating class */
    __attr attrs[];             /* attributes */
} __obj;

typedef __obj * __ref;

/* Fragments are simple collections of attributes employed by sequence types.
   They provide the basis of lists and tuples. */

typedef struct __fragment
{
    unsigned int size, capacity;
    __attr attrs[];
} __fragment;

#define __FRAGMENT_SIZE(NUMBER) (NUMBER * sizeof(__attr) + 2 * sizeof(unsigned int))

/* Special instance position value. The pos member of __obj refers to the
   special type attribute for classes, indicating which position holds the
   attribute describing the class type. For instances, it is set to zero. */

#define __INSTANCEPOS 0

/* Special null values. */

#define __NULL ((__attr) {{0}, {0}})

/* Function pointer type. */

typedef __attr (*__func)();

/* Convenience macros. */

#define __ARGS(...) ((__attr[]) {__VA_ARGS__})
#define __KWARGS(...) ((__param[]) {__VA_ARGS__})

#endif /* __TYPES_H__ */

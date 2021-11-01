/* Runtime types.

Copyright (C) 2015, 2016, 2017, 2018, 2019,
              2021 Paul Boddie <paul@boddie.org.uk>

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

/* Define code and position types, populated by enum values defined for each
   program specifically. */

#include <stdint.h>
#include <stdlib.h>

/* Include the special instance position value. The pos member of __obj refers
   to the special type attribute for classes, indicating which position holds
   the attribute describing the class type. For instances, it is set to the same
   attribute position as __class__ and is defined in the following file. */

#include "instancepos.h"

typedef uint16_t __code;
typedef uint16_t __pos;
typedef uint16_t __pcode;
typedef uint16_t __ppos;

/* Attribute tables are lists of codes confirming the presence of attributes. */

typedef struct __table
{
    const __pos size;
    const __code attrs[];
} __table;

/* Parameter tables are lists of codes confirming the presence of parameters, as
   well as the positions of those parameters in the list for a given function.
*/

typedef struct __param
{
    __code code;
    __pos pos;
} __param;

typedef struct __ptable
{
    const __ppos min, max, size;
    const __param params[];
} __ptable;

/* Attributes are values referring to objects or encoding other information.
   Objects are collections of attributes.
   Object references are references to tables and collections of attributes.
   Attribute references are references to single attributes. */

typedef struct __obj __obj;
typedef struct __fragment __fragment;
typedef union __attr __attr;
typedef __obj * __ref;

/* Introduce an integer type that should not exceed the size of the pointer
   type. */

typedef ssize_t __int;

/* Attribute value interpretations. */

typedef union __attr
{
    /* General attribute members. */

    __ref value;                /* attribute value */
    __int intvalue;             /* integer value data (shifted value, tagged) */

    /* Special case attribute members. */

    const __ptable * ptable;    /* parameter table */
    struct {
        __pcode code;           /* parameter table code for key */
        __ppos pos;             /* parameter table position for key */
    };
    __attr (*fn)();             /* callable details */
    char * strvalue;            /* string value */
    __fragment * seqvalue;      /* sequence data */
    void * datavalue;           /* object-specific data */
} __attr;

typedef struct __obj
{
    const __table * table;      /* attribute table */
    __ppos pos;                 /* position of attribute indicating class */
    __attr attrs[];             /* attributes */

    /* Specialisations of this type may add other members.
       See generator.py for type generation, progops.h for definitions, and
       the generated progtypes.h for the final details. */

} __obj;

#define __INSTANCE_SIZE(NUMBER) ((NUMBER) * sizeof(__attr) + sizeof(__table *) + sizeof(__ppos))

/* Fragments are simple collections of attributes employed by sequence types.
   They provide the basis of lists and tuples. */

typedef struct __fragment
{
    __int size, capacity;
    __attr attrs[];
} __fragment;

#define __FRAGMENT_SIZE(NUMBER) ((NUMBER) * sizeof(__attr) + 2 * sizeof(__int))

/* Attribute interpretation. */

#define __NUM_TAG_BITS      2
#define __TAG_INT           0b01
#define __TAG_MASK          0b11
#define __INTEGER(ATTR)     (((ATTR).intvalue & __TAG_MASK) == __TAG_INT)

/* Attribute value setting. */

#define __ATTRVALUE(VALUE)  ((__attr) {.value=(__ref) VALUE})
#define __NULL              __ATTRVALUE(0)
#define __SETNULL(ATTR)     ((ATTR).value = 0)

/* Attribute as instance setting. */

#define __INTVALUE(VALUE)   ((__attr) {.intvalue=(((__int) VALUE) << __NUM_TAG_BITS) | __TAG_INT})
#define __TOINT(ATTR)       ((ATTR).intvalue >> __NUM_TAG_BITS)
#define __MAXINT            ((((__int) 1) << ((sizeof(__int) * 8) - 1 - __NUM_TAG_BITS)) - 1)
#define __MININT            (-(((__int) 1) << ((sizeof(__int) * 8) - 1 - __NUM_TAG_BITS)))

/* Argument lists. */

#define __ARGS(...)         ((__attr[]) {__VA_ARGS__})
#define __KWARGS(...)       ((__param[]) {__VA_ARGS__})

/* Attribute codes and positions for attribute names. */

#define __ATTRCODE(ATTRNAME)    __code_##ATTRNAME
#define __ATTRPOS(ATTRNAME)     __pos_##ATTRNAME
#define __PARAMCODE(PARAMNAME)  __pcode_##PARAMNAME
#define __PARAMPOS(PARAMNAME)   __ppos_##PARAMNAME

#endif /* __TYPES_H__ */

/* Common operations.

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

#include "gc.h" /* GC_MALLOC, GC_REALLOC */
#include "ops.h"
#include "progops.h" /* for raising errors */
#include "progconsts.h"
#include "progtypes.h"

/* Direct access and manipulation of static objects. */

__attr __load_static(__ref parent, __ref obj)
{
    __attr out = {.context=parent, .value=obj};
    return out;
}

/* Direct retrieval operations, returning and setting attributes. */

__attr __load_via_object(__ref obj, int pos)
{
    return obj->attrs[pos];
}

__attr __load_via_class(__ref obj, int pos)
{
    return __load_via_object(__get_class(obj), pos);
}

__attr __get_class_and_load(__ref obj, int pos)
{
    if (__is_instance(obj))
        return __load_via_class(obj, pos);
    else
        return __load_via_object(obj, pos);
}

/* Direct storage operations. */

int __store_via_object(__ref obj, int pos, __attr value)
{
    obj->attrs[pos] = value;
    return 1;
}

int __get_class_and_store(__ref obj, int pos, __attr value)
{
    /* Forbid class-relative assignments. */

    __raise_type_error();
    return 0;
}

/* Introspection. */

int __is_instance(__ref obj)
{
    return obj->pos == __INSTANCEPOS;
}

int __is_type_instance(__ref obj)
{
    return __HASATTR(__get_class(obj), __TYPE_CLASS_POS, __TYPE_CLASS_CODE);
}

__ref __get_class(__ref obj)
{
    return __load_via_object(obj, __pos___class__).value;
}

__attr __get_class_attr(__ref obj)
{
    return __load_via_object(obj, __pos___class__);
}

/* Attribute testing operations. */

__ref __test_specific_instance(__ref obj, __ref type)
{
    return __get_class(obj) == type ? obj : 0;
}

__ref __test_specific_object(__ref obj, __ref type)
{
    return __test_specific_type(obj, type) || __test_specific_instance(obj, type) ? obj : 0;
}

__ref __test_specific_type(__ref obj, __ref type)
{
    return obj == type ? obj : 0;
}

__ref __test_common_instance(__ref obj, int pos, int code)
{
    return __HASATTR(__get_class(obj), pos, code) ? obj : 0;
}

__ref __test_common_object(__ref obj, int pos, int code)
{
    return __test_common_type(obj, pos, code) || __test_common_instance(obj, pos, code) ? obj : 0;
}

__ref __test_common_type(__ref obj, int pos, int code)
{
    return __HASATTR(obj, pos, code) ? obj : 0;
}

/* Attribute testing and retrieval operations. */

static __attr __check_and_load_via_object_null(__ref obj, int pos, int code)
{
    if (__HASATTR(obj, pos, code))
        return __load_via_object(obj, pos);
    else
        return __NULL;
}

__attr __check_and_load_via_class(__ref obj, int pos, int code)
{
    return __check_and_load_via_object(__get_class(obj), pos, code);
}

__attr __check_and_load_via_object(__ref obj, int pos, int code)
{
    if (__HASATTR(obj, pos, code))
        return __load_via_object(obj, pos);

    __raise_type_error();
    return __NULL;
}

__attr __check_and_load_via_any(__ref obj, int pos, int code)
{
    __attr out = __check_and_load_via_object_null(obj, pos, code);
    if (out.value == 0)
        out = __check_and_load_via_class(obj, pos, code);
    return out;
}

/* Attribute testing and storage operations. */

int __check_and_store_via_class(__ref obj, int pos, int code, __attr value)
{
    /* Forbid class-relative assignments. */

    __raise_type_error();
    return 0;
}

int __check_and_store_via_object(__ref obj, int pos, int code, __attr value)
{
    if (__HASATTR(obj, pos, code))
    {
        __store_via_object(obj, pos, value);
        return 1;
    }

    /* No suitable attribute. */

    __raise_type_error();
    return 0;
}

int __check_and_store_via_any(__ref obj, int pos, int code, __attr value)
{
    if (__check_and_store_via_object(obj, pos, code, value))
        return 1;

    /* Forbid class-relative assignments. */

    __raise_type_error();
    return 0;
}

/* Context-related operations. */

__attr __test_context(__ref context, __attr attr)
{
    /* Preserve any existing null or instance context. */

    if ((attr.context == 0) || __is_instance(attr.context))
        return attr;

    /* Test any instance context against the context employed by the
       attribute. */

    if (__is_instance(context))
        if (__test_common_instance(context, __TYPEPOS(attr.context), __TYPECODE(attr.context)))
            return __replace_context(context, attr);
        else
            __raise_type_error();

    /* Test for access to a type class attribute using a type instance. */

    if (__test_specific_type(attr.context, &__TYPE_CLASS_TYPE) && __is_type_instance(context))
        return __replace_context(context, attr);

    /* Otherwise, preserve the attribute as retrieved. */

    return attr;
}

__attr __replace_context(__ref context, __attr attr)
{
    __attr out;

    /* Set the context. */

    out.context = context;

    /* Reference a callable version of the attribute by obtaining the bound
       method reference from the __fn__ special attribute. */

    out.value = __load_via_object(attr.value, __ATTRPOS(__fn__)).b;
    return out;
}

__attr __update_context(__ref context, __attr attr)
{
    __attr out = {context, .fn=attr.fn};
    return out;
}

/* Basic structure tests. */

int __WITHIN(__ref obj, int pos)
{
    return pos < obj->table->size;
}

int __HASATTR(__ref obj, int pos, int code)
{
    return __WITHIN(obj, pos) && (obj->table->attrs[pos] == code);
}

/* Parameter position operations. */

int __HASPARAM(const __ptable *ptable, int ppos, int pcode)
{
    __param param;

    if (ppos < ptable->size)
    {
        param = ptable->params[ppos];
        if (param.code == pcode)
            return param.pos;
    }

    return -1;
}

/* Conversions. */

__attr __CONTEXT_AS_VALUE(__attr attr)
{
    __attr out;
    out.context = attr.context;
    out.value = attr.context;
    return out;
}

/* Type testing. */

__ref __ISFUNC(__ref obj)
{
    return __test_specific_instance(obj, &__FUNCTION_TYPE);
}

int __ISNULL(__attr value)
{
    /* (value.context == __NULL.context) is superfluous */
    return (value.value == 0); /* __NULL.value */
}

/* Attribute codes and positions for type objects. */

unsigned int __TYPECODE(__ref obj)
{
    return obj->table->attrs[obj->pos];
}

unsigned int __TYPEPOS(__ref obj)
{
    return obj->pos;
}

/* Memory allocation. */

void *__ALLOCATE(size_t nmemb, size_t size)
{
    void *ptr = GC_MALLOC(nmemb * size); /* sets memory to zero */
    if (ptr == NULL)
        __raise_memory_error();
    return ptr;
}

void *__REALLOCATE(void *ptr, size_t size)
{
    void *nptr = GC_REALLOC(ptr, size);
    if (nptr == NULL)
        __raise_memory_error();
    return nptr;
}

/* Copying of structures. */

__ref __COPY(__ref obj, int size)
{
    __ref copy = (__ref) __ALLOCATE(1, size);
    memcpy(copy, obj, size);
    return copy;
}

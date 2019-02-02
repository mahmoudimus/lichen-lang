/* Common operations.

Copyright (C) 2015, 2016, 2017, 2018 Paul Boddie <paul@boddie.org.uk>

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
#include "types.h"
#include "ops.h"
#include "progops.h" /* for raising errors */
#include "progconsts.h"
#include "progtypes.h"

/* Get object reference from attribute. */

__ref __VALUE(__attr attr)
{
    if (!__INTEGER(attr))
        return attr.value;
    else
        return &__common_integer_obj;
}

/* Basic structure tests. */

static inline int __HASATTR(__ref obj, int pos, int code)
{
    return (pos < obj->table->size) && (obj->table->attrs[pos] == code);
}

/* Direct access and manipulation of static objects. */

__attr __load_static_ignore(__ref obj)
{
    return __ATTRVALUE(obj);
}

__attr __load_static_replace(__attr context, __ref obj)
{
    return __update_context(context, __ATTRVALUE(obj));
}

__attr __load_static_test(__attr context, __ref obj)
{
    return __test_context(context, __ATTRVALUE(obj));
}

/* Direct retrieval operations, returning and setting attributes. */

__attr __load_via_object__(__ref obj, int pos)
{
    return obj->attrs[pos];
}

__attr __load_via_class__(__ref obj, int pos)
{
    return __load_via_object__(__get_class(obj), pos);
}

__attr __get_class_and_load__(__ref obj, int pos)
{
    if (__is_instance(obj))
        return __load_via_class__(obj, pos);
    else
        return __load_via_object__(obj, pos);
}

/* Direct storage operations. */

int __store_via_object__(__ref obj, int pos, __attr value)
{
    obj->attrs[pos] = value;
    return 1;
}

int __store_via_class__(__ref obj, int pos, __attr value)
{
    return __store_via_object__(__get_class(obj), pos, value);
}

int __get_class_and_store__(__ref obj, int pos, __attr value)
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

int __is_subclass(__ref obj, __attr cls)
{
    return __HASATTR(obj, __TYPEPOS(__VALUE(cls)), __TYPECODE(__VALUE(cls)));
}

int __is_instance_subclass(__ref obj, __attr cls)
{
    return __is_instance(obj) && __HASATTR(__get_class(obj), __TYPEPOS(__VALUE(cls)), __TYPECODE(__VALUE(cls)));
}

int __is_type_instance(__ref obj)
{
    return __HASATTR(__get_class(obj), __TYPE_CLASS_POS, __TYPE_CLASS_CODE);
}

__ref __get_class(__ref obj)
{
    return __VALUE(__load_via_object(obj, __class__));
}

__attr __get_class_attr(__ref obj)
{
    return __load_via_object(obj, __class__);
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

__ref __test_common_instance__(__ref obj, int pos, int code)
{
    return __HASATTR(__get_class(obj), pos, code) ? obj : 0;
}

__ref __test_common_object__(__ref obj, int pos, int code)
{
    return __test_common_type__(obj, pos, code) || __test_common_instance__(obj, pos, code) ? obj : 0;
}

__ref __test_common_type__(__ref obj, int pos, int code)
{
    return __HASATTR(obj, pos, code) ? obj : 0;
}

/* Attribute testing and retrieval operations. */

__attr __check_and_load_via_object_null(__ref obj, int pos, int code)
{
    if (__HASATTR(obj, pos, code))
        return __load_via_object__(obj, pos);
    else
        return __NULL;
}

__attr __check_and_load_via_class__(__ref obj, int pos, int code)
{
    return __check_and_load_via_object__(__get_class(obj), pos, code);
}

__attr __check_and_load_via_object__(__ref obj, int pos, int code)
{
    if (__HASATTR(obj, pos, code))
        return __load_via_object__(obj, pos);

    __raise_type_error();
    return __NULL;
}

__attr __check_and_load_via_any__(__ref obj, int pos, int code)
{
    __attr out = __check_and_load_via_object_null(obj, pos, code);
    if (__ISNULL(out))
        out = __check_and_load_via_class__(obj, pos, code);
    return out;
}

/* Attribute testing and storage operations. */

int __check_and_store_via_class__(__ref obj, int pos, int code, __attr value)
{
    /* Forbid class-relative assignments. */

    __raise_type_error();
    return 0;
}

int __check_and_store_via_object__(__ref obj, int pos, int code, __attr value)
{
    if (__HASATTR(obj, pos, code))
    {
        __store_via_object__(obj, pos, value);
        return 1;
    }

    /* No suitable attribute. */

    __raise_type_error();
    return 0;
}

int __check_and_store_via_any__(__ref obj, int pos, int code, __attr value)
{
    if (__check_and_store_via_object__(obj, pos, code, value))
        return 1;

    /* Forbid class-relative assignments. */

    __raise_type_error();
    return 0;
}

/* Context-related operations. */

int __test_context_update(__attr context, __attr attr, int invoke)
{
    /* Return whether the context should be updated for the attribute. */

    __attr attrcontext = __CONTEXT_AS_VALUE(attr);
    __ref attrcontextvalue = __VALUE(attrcontext);

    /* Preserve any existing null or instance context. */

    if (__ISNULL(attrcontext) || __is_instance(attrcontextvalue))
        return 0;

    /* Test any instance context against the context employed by the
       attribute. */

    if (__is_instance(__VALUE(context)))
    {
        /* Obtain the special class attribute position and code identifying the
           attribute context's class, inspecting the context instance for
           compatibility. */

        if (__test_common_instance__(__VALUE(context), __TYPEPOS(attrcontextvalue), __TYPECODE(attrcontextvalue)))
            return 1;
        else
            __raise_type_error();
    }

    /* Without a null or instance context, an invocation cannot be performed. */

    if (invoke)
        __raise_unbound_method_error();

    /* Test for access to a type class attribute using a type instance. */

    if (__test_specific_type(attrcontextvalue, &__TYPE_CLASS_TYPE) && __is_type_instance(__VALUE(context)))
        return 1;

    /* Otherwise, preserve the attribute as retrieved. */

    return 0;
}

__attr __test_context(__attr context, __attr attr)
{
    /* Update the context or return the unchanged attribute. */

    if (__test_context_update(context, attr, 0))
        return __update_context(context, attr);
    else
        return attr;
}

__attr __update_context(__attr context, __attr attr)
{
    return __new_wrapper(context, attr);
}

__attr __test_context_revert(int target, __attr context, __attr attr, __attr contexts[])
{
    /* Revert the local context to that employed by the attribute if the
       supplied context is not appropriate. */

    if (!__test_context_update(context, attr, 1))
        contexts[target] = __CONTEXT_AS_VALUE(attr);
    return attr;
}

__attr __test_context_static(int target, __attr context, __ref value, __attr contexts[])
{
    /* Set the local context to the specified context if appropriate. */

    if (__test_context_update(context, __ATTRVALUE(value), 1))
        contexts[target] = context;
    return __ATTRVALUE(value);
}

/* Context testing for invocations. */

int __type_method_invocation(__attr context, __attr target)
{
    __attr targetcontext = __CONTEXT_AS_VALUE(target);

    /* Require instances, not classes, where methods are function instances. */

    if (!__is_instance(__VALUE(target)))
        return 0;

    /* Access the context of the callable and test if it is the type object. */

    return (!__ISNULL(targetcontext) && __test_specific_type(__VALUE(targetcontext), &__TYPE_CLASS_TYPE) && __is_type_instance(__VALUE(context)));
}

__attr __unwrap_callable(__attr callable)
{
    __attr value = __check_and_load_via_object_null(__VALUE(callable), __ATTRPOS(__value__), __ATTRCODE(__value__));
    return __VALUE(value) ? value : callable;
}

__attr (*__get_function_unchecked(__attr target))()
{
    return __load_via_object(__VALUE(__unwrap_callable(target)), __fn__).fn;
}

__attr (*__get_function(__attr context, __attr target))()
{
    return __get_function_unwrapped(context, __unwrap_callable(target));
}

__attr (*__get_function_unwrapped(__attr context, __attr target))()
{
    /* Require null or instance contexts for functions and methods respectively,
       or type instance contexts for type methods. */

    if (__ISNULL(context) || __is_instance(__VALUE(context)) || __type_method_invocation(context, target))
        return __get_function_member(target);
    else
        return __unbound_method;
}

__attr (*__get_function_member(__attr target))()
{
    return __load_via_object(__VALUE(target), __fn__).fn;
}

__attr (*__check_and_get_function(__attr context, __attr target))()
{
    return __check_and_get_function_unwrapped(context, __unwrap_callable(target));
}

__attr (*__check_and_get_function_unwrapped(__attr context, __attr target))()
{
    /* Require null or instance contexts for functions and methods respectively,
       or type instance contexts for type methods. */

    if (__ISNULL(context) || __is_instance(__VALUE(context)) || __type_method_invocation(context, target))
        return __check_and_load_via_object__(__VALUE(target), __ATTRPOS(__fn__), __ATTRCODE(__fn__)).fn;
    else
        return __unbound_method;
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
    return __check_and_load_via_object_null(__VALUE(attr), __ATTRPOS(__context__), __ATTRCODE(__context__));
}

/* Type testing. */

__ref __ISFUNC(__ref obj)
{
    return __test_specific_instance(obj, &__FUNCTION_TYPE);
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

void *__ALLOCATEIM(size_t nmemb, size_t size)
{
    void *ptr = GC_MALLOC_ATOMIC(nmemb * size); /* sets memory to zero */
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

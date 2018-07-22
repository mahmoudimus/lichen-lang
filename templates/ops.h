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

#ifndef __OPS_H__
#define __OPS_H__

#include "types.h"
#include <string.h> /* for __COPY */

/* Get object reference from attribute. */

__ref __VALUE(__attr attr);

/* Direct access and manipulation of static objects. */

__attr __load_static_ignore(__ref obj);
__attr __load_static_replace(__attr context, __ref obj);
__attr __load_static_test(__attr context, __ref obj);

/* Direct retrieval operations, returning attributes. */

__attr __load_via_class__(__ref obj, int pos);
__attr __load_via_object__(__ref obj, int pos);
__attr __get_class_and_load__(__ref obj, int pos);

#define __load_via_class(OBJ, ATTRNAME) (__load_via_class__(OBJ, __ATTRPOS(ATTRNAME)))
#define __load_via_object(OBJ, ATTRNAME) (__load_via_object__(OBJ, __ATTRPOS(ATTRNAME)))
#define __get_class_and_load(OBJ, ATTRNAME) (__get_class_and_load__(OBJ, __ATTRPOS(ATTRNAME)))

/* Direct storage operations. */

int __store_via_class__(__ref obj, int pos, __attr value);
int __store_via_object__(__ref obj, int pos, __attr value);
int __get_class_and_store__(__ref obj, int pos, __attr value);

#define __store_via_class(OBJ, ATTRNAME, VALUE) (__store_via_class__(OBJ, __ATTRPOS(ATTRNAME), VALUE))
#define __store_via_object(OBJ, ATTRNAME, VALUE) (__store_via_object__(OBJ, __ATTRPOS(ATTRNAME), VALUE))
#define __get_class_and_store(OBJ, ATTRNAME, VALUE) (__get_class_and_store__(OBJ, __ATTRPOS(ATTRNAME), VALUE))

/* Introspection. */

int __is_instance(__ref obj);
int __is_subclass(__ref obj, __attr cls);
int __is_instance_subclass(__ref obj, __attr cls);
int __is_type_instance(__ref obj);
__ref __get_class(__ref obj);
__attr __get_class_attr(__ref obj);

/* Attribute testing operations. */

__ref __test_specific_instance(__ref obj, __ref type);
__ref __test_specific_object(__ref obj, __ref type);
__ref __test_specific_type(__ref obj, __ref type);

__ref __test_common_instance__(__ref obj, int pos, int code);
__ref __test_common_object__(__ref obj, int pos, int code);
__ref __test_common_type__(__ref obj, int pos, int code);

#define __to_error(REF) (REF ? REF : (__raise_type_error(), (__ref) 0))

#define __test_common_instance(OBJ, TYPENAME) (__test_common_instance__(OBJ, __ATTRPOS(TYPENAME), __ATTRCODE(TYPENAME)))
#define __test_common_object(OBJ, TYPENAME) (__test_common_object__(OBJ, __ATTRPOS(TYPENAME), __ATTRCODE(TYPENAME)))
#define __test_common_type(OBJ, TYPENAME) (__test_common_type__(OBJ, __ATTRPOS(TYPENAME), __ATTRCODE(TYPENAME)))

/* Attribute testing and retrieval operations. */

__attr __check_and_load_via_object_null(__ref obj, int pos, int code);

__attr __check_and_load_via_class__(__ref obj, int pos, int code);
__attr __check_and_load_via_object__(__ref obj, int pos, int code);
__attr __check_and_load_via_any__(__ref obj, int pos, int code);

#define __check_and_load_via_class(OBJ, ATTRNAME) (__check_and_load_via_class__(OBJ, __ATTRPOS(ATTRNAME), __ATTRCODE(ATTRNAME)))
#define __check_and_load_via_object(OBJ, ATTRNAME) (__check_and_load_via_object__(OBJ, __ATTRPOS(ATTRNAME), __ATTRCODE(ATTRNAME)))
#define __check_and_load_via_any(OBJ, ATTRNAME) (__check_and_load_via_any__(OBJ, __ATTRPOS(ATTRNAME), __ATTRCODE(ATTRNAME)))

/* Attribute testing and storage operations. */

int __check_and_store_via_class__(__ref obj, int pos, int code, __attr value);
int __check_and_store_via_object__(__ref obj, int pos, int code, __attr value);
int __check_and_store_via_any__(__ref obj, int pos, int code, __attr value);

#define __check_and_store_via_class(OBJ, ATTRNAME, VALUE) (__check_and_store_via_class__(OBJ, __ATTRPOS(ATTRNAME), __ATTRCODE(ATTRNAME), VALUE))
#define __check_and_store_via_object(OBJ, ATTRNAME, VALUE) (__check_and_store_via_object__(OBJ, __ATTRPOS(ATTRNAME), __ATTRCODE(ATTRNAME), VALUE))
#define __check_and_store_via_any(OBJ, ATTRNAME, VALUE) (__check_and_store_via_any__(OBJ, __ATTRPOS(ATTRNAME), __ATTRCODE(ATTRNAME), VALUE))

/* Context-related operations. */

int __test_context_update(__attr context, __attr attr, int invoke);
__attr __test_context(__attr context, __attr attr);
__attr __update_context(__attr context, __attr attr);
__attr __test_context_revert(int target, __attr context, __attr attr, __attr contexts[]);
__attr __test_context_static(int target, __attr context, __ref value, __attr contexts[]);

#define __get_accessor(__TARGET) (__tmp_values[__TARGET])
#define __get_context(__TARGET) (__tmp_contexts[__TARGET])
#define __set_context(__TARGET, __ATTR) (__tmp_contexts[__TARGET] = (__ATTR))
#define __set_private_context(__ATTR) (__tmp_private_context = (__ATTR))
#define __set_accessor(__TARGET, __ATTR) (__tmp_values[__TARGET] = (__ATTR))
#define __set_target_accessor(__ATTR) (__tmp_target_value = (__ATTR))

/* Context testing for invocations. */

__attr __unwrap_callable(__attr callable);
__attr (*__get_function_unchecked(__attr target))();
__attr (*__get_function(__attr context, __attr target))();
__attr (*__get_function_unwrapped(__attr context, __attr target))();
__attr (*__get_function_member(__attr target))();
__attr (*__check_and_get_function(__attr context, __attr target))();
__attr (*__check_and_get_function_unwrapped(__attr context, __attr target))();

/* Parameter position operations. */

int __HASPARAM(const __ptable *ptable, int ppos, int pcode);

/* Conversions. */

__attr __CONTEXT_AS_VALUE(__attr attr);

/* Type testing. */

__ref __ISFUNC(__ref obj);
int __ISNULL(__attr value);

/* Attribute codes and positions for type objects. */

unsigned int __TYPECODE(__ref obj);
unsigned int __TYPEPOS(__ref obj);

/* Memory allocation. */

void *__ALLOCATE(size_t nmemb, size_t size);
void *__ALLOCATEIM(size_t nmemb, size_t size);
void *__REALLOCATE(void *ptr, size_t size);

/* Copying of structures. */

__ref __COPY(__ref obj, int size);

#endif /* __OPS_H__ */

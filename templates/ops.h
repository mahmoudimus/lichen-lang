/* Common operations.

Copyright (C) 2015, 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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

/* Direct access and manipulation of static objects. */

__attr __load_static_ignore(__ref obj);
__attr __load_static_replace(__ref context, __ref obj);
__attr __load_static_test(__ref context, __ref obj);

/* Direct retrieval operations, returning attributes. */

__attr __load_via_class(__ref obj, int pos);
__attr __load_via_object(__ref obj, int pos);
__attr __get_class_and_load(__ref obj, int pos);

/* Direct storage operations. */

int __store_via_object(__ref obj, int pos, __attr value);
int __get_class_and_store(__ref obj, int pos, __attr value);

/* Introspection. */

int __is_instance(__ref obj);
int __is_type_instance(__ref obj);
__ref __get_class(__ref obj);
__attr __get_class_attr(__ref obj);

/* Attribute testing operations. */

__ref __test_specific_instance(__ref obj, __ref type);
__ref __test_specific_object(__ref obj, __ref type);
__ref __test_specific_type(__ref obj, __ref type);
__ref __test_common_instance(__ref obj, int pos, int code);
__ref __test_common_object(__ref obj, int pos, int code);
__ref __test_common_type(__ref obj, int pos, int code);

/* Attribute testing and retrieval operations. */

__attr __check_and_load_via_class(__ref obj, int pos, int code);
__attr __check_and_load_via_object(__ref obj, int pos, int code);
__attr __check_and_load_via_object_null(__ref obj, int pos, int code);
__attr __check_and_load_via_any(__ref obj, int pos, int code);

/* Attribute testing and storage operations. */

int __check_and_store_via_class(__ref obj, int pos, int code, __attr value);
int __check_and_store_via_object(__ref obj, int pos, int code, __attr value);
int __check_and_store_via_any(__ref obj, int pos, int code, __attr value);

/* Context-related operations. */

int __test_context_update(__ref context, __attr attr);
__attr __test_context(__ref context, __attr attr);
__attr __update_context(__ref context, __attr attr);
__attr __test_context_revert(int target, __ref context, __attr attr, __ref contexts[]);
__attr __test_context_static(int target, __ref context, __ref value, __ref contexts[]);

#define __get_context(__TARGET) (__tmp_contexts[__TARGET])
#define __set_context(__TARGET, __ATTR) (__tmp_contexts[__TARGET] = (__ATTR).value)
#define __set_private_context(__ATTR) (__tmp_private_context = (__ATTR).value)
#define __set_accessor(__ATTR) (__tmp_value = (__ATTR).value)
#define __set_target_accessor(__ATTR) (__tmp_target_value = (__ATTR).value)

/* Context testing for invocations. */

__attr __unwrap_callable(__attr callable);
__attr (*__get_function(__ref context, __attr target))(__attr[]);
__attr (*__check_and_get_function(__ref context, __attr target))(__attr[]);

/* Basic structure tests. */

int __WITHIN(__ref obj, int pos);
int __HASATTR(__ref obj, int pos, int code);

/* Parameter position operations. */

int __HASPARAM(const __ptable *ptable, int ppos, int pcode);

/* Conversions. */

__attr __CONTEXT_AS_VALUE(__attr attr);

/* Type testing. */

__ref __ISFUNC(__ref obj);
int __ISNULL(__attr value);

/* __TEST(obj, __A) -> test obj for the special type attribute __A */

#define __TEST(__OBJ, __TYPE) (__test_common_instance(__OBJ, __pos_##__TYPE, __code_##__TYPE))

/* Attribute codes and positions for type objects. */

unsigned int __TYPECODE(__ref obj);
unsigned int __TYPEPOS(__ref obj);

/* Memory allocation. */

void *__ALLOCATE(size_t nmemb, size_t size);
void *__REALLOCATE(void *ptr, size_t size);

/* Copying of structures. */

__ref __COPY(__ref obj, int size);

#endif /* __OPS_H__ */

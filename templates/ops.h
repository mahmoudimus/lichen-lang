/* Common operations. */

#ifndef __OPS_H__
#define __OPS_H__

#include "types.h"
#include <string.h> /* for __COPY */

/* Direct access to functions. */

__attr __load_function(__func fn);

/* Direct access and manipulation of static objects. */

__attr __load_static(__ref obj);

/* Direct retrieval operations, returning attributes. */

__attr __load_via_class(__ref obj, int pos);
__attr __load_via_object(__ref obj, int pos);

/* Direct storage operations. */

int __store_via_object(__ref obj, int pos, __attr value);

/* Introspection. */

int __is_instance(__ref obj);
__ref __get_class(__ref obj);

/* Attribute testing operations. */

__ref __test_common_instance(__ref obj, int pos, int code);
__ref __test_common_object(__ref obj, int pos, int code);
__ref __test_common_type(__ref obj, int pos, int code);
__ref __test_specific_instance(__ref obj, __ref type);

/* Attribute testing and retrieval operations. */

__attr __check_and_load_via_class(__ref obj, int pos, int code);
__attr __check_and_load_via_object(__ref obj, int pos, int code);
__attr __check_and_load_via_any(__ref obj, int pos, int code);

/* Attribute testing and storage operations. */

int __check_and_store_via_object(__ref obj, int pos, int code, __attr value);
int __check_and_store_via_any(__ref obj, int pos, int code, __attr value);

/* Context-related operations. */

__attr __test_context(__ref context, __attr attr);
__attr __replace_context(__ref context, __attr attr);
__attr __update_context(__ref context, __attr attr);

#define __set_context(__ATTR) (__tmp_context = (__ATTR).value)
#define __set_accessor(__ATTR) (__tmp_value = (__ATTR).value)

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

/* Attribute codes and positions for attribute names. */

#define __ATTRCODE(__ATTRNAME) (__code_##__ATTRNAME)
#define __ATTRPOS(__ATTRNAME) (__pos_##__ATTRNAME)

/* Copying of structures. */

#define __COPY(__SOURCE, __TARGET) (memcpy(__TARGET, __SOURCE, sizeof(__SOURCE)))

#endif /* __OPS_H__ */

#ifndef __NATIVE_H__
#define __NATIVE_H__

/* Native functions. */

__attr __fn_native__exit(__attr __args[]);
__attr __fn_native__get_argv(__attr __args[]);
__attr __fn_native__get_path(__attr __args[]);

__attr __fn_native__is(__attr __args[]);
__attr __fn_native__is_not(__attr __args[]);

__attr __fn_native__get_maxint(__attr __args[]);
__attr __fn_native__get_minint(__attr __args[]);

__attr __fn_native__int_add(__attr __args[]);
__attr __fn_native__int_div(__attr __args[]);
__attr __fn_native__int_mod(__attr __args[]);
__attr __fn_native__int_mul(__attr __args[]);
__attr __fn_native__int_neg(__attr __args[]);
__attr __fn_native__int_pow(__attr __args[]);
__attr __fn_native__int_sub(__attr __args[]);

__attr __fn_native__int_and(__attr __args[]);
__attr __fn_native__int_not(__attr __args[]);
__attr __fn_native__int_or(__attr __args[]);
__attr __fn_native__int_xor(__attr __args[]);

__attr __fn_native__int_rdiv(__attr __args[]);
__attr __fn_native__int_rmod(__attr __args[]);
__attr __fn_native__int_rpow(__attr __args[]);
__attr __fn_native__int_rsub(__attr __args[]);

__attr __fn_native__int_lt(__attr __args[]);
__attr __fn_native__int_gt(__attr __args[]);
__attr __fn_native__int_eq(__attr __args[]);
__attr __fn_native__int_ne(__attr __args[]);

__attr __fn_native__int_str(__attr __args[]);

__attr __fn_native__str_add(__attr __args[]);
__attr __fn_native__str_lt(__attr __args[]);
__attr __fn_native__str_gt(__attr __args[]);
__attr __fn_native__str_eq(__attr __args[]);
__attr __fn_native__str_len(__attr __args[]);
__attr __fn_native__str_nonempty(__attr __args[]);
__attr __fn_native__str_ord(__attr __args[]);
__attr __fn_native__str_substr(__attr __args[]);

__attr __fn_native__list_init(__attr __args[]);
__attr __fn_native__list_setsize(__attr __args[]);
__attr __fn_native__list_append(__attr __args[]);
__attr __fn_native__list_concat(__attr __args[]);
__attr __fn_native__list_len(__attr __args[]);
__attr __fn_native__list_nonempty(__attr __args[]);
__attr __fn_native__list_element(__attr __args[]);
__attr __fn_native__list_setelement(__attr __args[]);

__attr __fn_native__buffer_str(__attr __args[]);

__attr __fn_native__get_using(__attr __args[]);

__attr __fn_native__object_getattr(__attr __args[]);

__attr __fn_native__isinstance(__attr __args[]);
__attr __fn_native__issubclass(__attr __args[]);

__attr __fn_native__read(__attr __args[]);
__attr __fn_native__write(__attr __args[]);

/* Module initialisation. */

void __main_native();

#endif /* __NATIVE_H__ */

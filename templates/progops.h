/* Program type definitions. */

#include <stdlib.h>
#include "types.h"

/* Common operations. */

__attr __new(const __table *table, __ref cls, size_t size);

__fragment *__new_fragment(unsigned int n);

__mapping *__new_mapping(unsigned int n);

void __newdata_sequence(__attr args[], unsigned int number);

void __newdata_mapping(__attr args[], unsigned int number);

__attr __invoke(__attr callable, int always_callable,
                unsigned int nkwargs, __param kwcodes[], __attr kwargs[],
                unsigned int nargs, __attr args[]);

/* Error routines. */

__attr __unbound_method(__attr args[]);

/* Generic operations depending on specific program details. */

void __SETDEFAULT(__ref obj, int pos, __attr value);

__attr __GETDEFAULT(__ref obj, int pos);

int __BOOL(__attr attr);

/*===
cexcept.h 2.0.1-Lichen (2016-Oct-27-Thu)
A modified form of...
cexcept.h 2.0.1 (2008-Jul-19-Sat)
http://www.nicemice.net/cexcept/
Adam M. Costello
http://www.nicemice.net/amc/

An interface for exception-handling in ANSI C (C89 and subsequent ISO
standards), developed jointly with Cosmin Truta. 

    Copyright (c) 2016 Paul Boddie (modified for Lichen).
    Copyright (c) 2000-2008 Adam M. Costello and Cosmin Truta.
    This software may be modified only if its author and version
    information is updated accurately, and may be redistributed
    only if accompanied by this unaltered notice.  Subject to those
    restrictions, permission is granted to anyone to do anything
    with this software.  The copyright holders make no guarantees
    regarding this software, and are not responsible for any damage
    resulting from its use.

The cexcept interface is not compatible with and cannot interact
with system exceptions (like division by zero or memory segmentation
violation), compiler-generated exceptions (like C++ exceptions), or
other exception-handling interfaces.

When using this interface across multiple .c files, do not include
this header file directly.  Instead, create a wrapper header file that
includes this header file and then invokes the define_exception_type
macro (see below).  The .c files should then include that header file.

The interface consists of one type, one well-known name, and six macros.


define_exception_type(type_name);

    This macro is used like an external declaration.  It specifies
    the type of object that gets copied from the exception thrower to
    the exception catcher.  The type_name can be any type that can be
    assigned to, that is, a non-constant arithmetic type, struct, union,
    or pointer.  Examples:

        define_exception_type(int);

        enum exception { out_of_memory, bad_arguments, disk_full };
        define_exception_type(enum exception);

        struct exception { int code; const char *msg; };
        define_exception_type(struct exception);

    Because throwing an exception causes the object to be copied (not
    just once, but twice), programmers may wish to consider size when
    choosing the exception type.


struct __exception_context;

    This type may be used after the define_exception_type() macro has
    been invoked.  A struct __exception_context must be known to both
    the thrower and the catcher.  It is expected that there be one
    context for each thread that uses exceptions.  It would certainly
    be dangerous for multiple threads to access the same context.
    One thread can use multiple contexts, but that is likely to be
    confusing and not typically useful.  The application can allocate
    this structure in any way it pleases--automatic, static, or dynamic.
    The application programmer should pretend not to know the structure
    members, which are subject to change.


struct __exception_context *__the_exception_context;

    The __Try/__Catch and __Throw statements (described below) implicitly
    refer to a context, using the name __the_exception_context.  It is
    the application's responsibility to make sure that this name yields
    the address of a mutable (non-constant) struct __exception_context
    wherever those statements are used.  Subject to that constraint, the
    application may declare a variable of this name anywhere it likes
    (inside a function, in a parameter list, or externally), and may
    use whatever storage class specifiers (static, extern, etc) or type
    qualifiers (const, volatile, etc) it likes.  Examples:

        static struct __exception_context
          * const __the_exception_context = &foo;

        { struct __exception_context *__the_exception_context = bar; ... }

        int blah(struct __exception_context *__the_exception_context, ...);

        extern struct __exception_context __the_exception_context[1];

    The last example illustrates a trick that avoids creating a pointer
    object separate from the structure object.

    The name could even be a macro, for example:

        struct __exception_context ec_array[numthreads];
        #define __the_exception_context (ec_array + thread_id)

    Be aware that __the_exception_context is used several times by the
    __Try/__Catch/__Throw macros, so it shouldn't be expensive or have side
    effects.  The expansion must be a drop-in replacement for an
    identifier, so it's safest to put parentheses around it.


void __init_exception_context(struct __exception_context *ec);

    For context structures allocated statically (by an external
    definition or using the "static" keyword), the implicit
    initialization to all zeros is sufficient, but contexts allocated
    by other means must be initialized using this macro before they
    are used by a __Try/__Catch statement.  It does no harm to initialize
    a context more than once (by using this macro on a statically
    allocated context, or using this macro twice on the same context),
    but a context must not be re-initialized after it has been used by a
    __Try/__Catch statement.


__Try statement
__Catch (expression) statement

    The __Try/__Catch/__Throw macros are capitalized in order to avoid
    confusion with the C++ keywords, which have subtly different
    semantics.

    A __Try/__Catch statement has a syntax similar to an if/else statement,
    except that the parenthesized expression goes after the second
    keyword rather than the first.  As with if/else, there are two
    clauses, each of which may be a simple statement ending with a
    semicolon or a brace-enclosed compound statement.  But whereas
    the else clause is optional, the __Catch clause is required.  The
    expression must be a modifiable lvalue (something capable of being
    assigned to) of the same type (disregarding type qualifiers) that
    was passed to define_exception_type().

    If a __Throw that uses the same exception context as the __Try/__Catch is
    executed within the __Try clause (typically within a function called
    by the __Try clause), and the exception is not caught by a nested
    __Try/__Catch statement, then a copy of the exception will be assigned
    to the expression, and control will jump to the __Catch clause.  If no
    such __Throw is executed, then the assignment is not performed, and
    the __Catch clause is not executed.

    The expression is not evaluated unless and until the exception is
    caught, which is significant if it has side effects, for example:

        __Try foo();
        __Catch (p[++i].e) { ... }

    IMPORTANT: Jumping into or out of a __Try clause (for example via
    return, break, continue, goto, longjmp) is forbidden--the compiler
    will not complain, but bad things will happen at run-time.  Jumping
    into or out of a __Catch clause is okay, and so is jumping around
    inside a __Try clause.  In many cases where one is tempted to return
    from a __Try clause, it will suffice to use __Throw, and then return
    from the __Catch clause.  Another option is to set a flag variable and
    use goto to jump to the end of the __Try clause, then check the flag
    after the __Try/__Catch statement.

    IMPORTANT: The values of any non-volatile automatic variables
    changed within the __Try clause are undefined after an exception is
    caught.  Therefore, variables modified inside the __Try block whose
    values are needed later outside the __Try block must either use static
    storage or be declared with the "volatile" type qualifier.


__Throw expression;

    A __Throw statement is very much like a return statement, except that
    the expression is required.  Whereas return jumps back to the place
    where the current function was called, __Throw jumps back to the __Catch
    clause of the innermost enclosing __Try clause.  The expression must
    be compatible with the type passed to define_exception_type().  The
    exception must be caught, otherwise the program may crash.

    Slight limitation:  If the expression is a comma-expression, it must
    be enclosed in parentheses.


__Try statement
__Catch_anonymous statement

    When the value of the exception is not needed, a __Try/__Catch statement
    can use __Catch_anonymous instead of __Catch (expression).


Everything below this point is for the benefit of the compiler.  The
application programmer should pretend not to know any of it, because it
is subject to change.

===*/


#ifndef CEXCEPT_H
#define CEXCEPT_H


#include <setjmp.h>

#define define_exception_type(etype) \
struct __exception_context { \
  jmp_buf *penv; \
  int caught; \
  volatile struct { etype etmp; } v; \
}

/* etmp must be volatile because the application might use automatic */
/* storage for __the_exception_context, and etmp is modified between   */
/* the calls to setjmp() and longjmp().  A wrapper struct is used to */
/* avoid warnings about a duplicate volatile qualifier in case etype */
/* already includes it.                                              */

#define __init_exception_context(ec) ((void)((ec)->penv = 0))

#define __Try \
  { \
    jmp_buf *exception__prev, exception__env; \
    exception__prev = __the_exception_context->penv; \
    __the_exception_context->penv = &exception__env; \
    if (setjmp(exception__env) == 0) { \
      do

#define exception__catch(action) \
      while (__the_exception_context->caught = 0, \
             __the_exception_context->caught); \
    } \
    else { \
      __the_exception_context->caught = 1; \
    } \
    __the_exception_context->penv = exception__prev; \
  } \
  if (!__the_exception_context->caught || action) { } \
  else

#define __Catch(e) exception__catch(((e) = __the_exception_context->v.etmp, 0))
#define __Catch_anonymous exception__catch(0)

/* __Try ends with do, and __Catch begins with while(0) and ends with     */
/* else, to ensure that __Try/__Catch syntax is similar to if/else        */
/* syntax.                                                            */
/*                                                                    */
/* The 0 in while(0) is expressed as x=0,x in order to appease        */
/* compilers that warn about constant expressions inside while().     */
/* Most compilers should still recognize that the condition is always */
/* false and avoid generating code for it.                            */

#define __Throw \
  for (;; longjmp(*__the_exception_context->penv, 1)) \
    __the_exception_context->v.etmp =


#endif /* CEXCEPT_H */

class C:

    "Class providing class and instance attributes."

    def __init__(self):
        self.a = 1

    def m(self, x):
        return x

class D:

    "An alternative class."

    pass

def getc():

    "Return an instance of C to test object suitability."

    return C()

def getd():

    "Return an instance of D to test object suitability."

    return D()

def f(obj, i):

    """
    Obtain an attribute on 'obj', performing an operation depending on 'i'.
    This tests attribute access and invocation.
    """

    if i:
        return obj.m(i)         # should cause access to an unbound method
    else:
        return obj.m

def g(obj, i):

    """
    Obtain an attribute on 'obj', performing an operation depending on 'i'.
    This tests attribute access and invocation, restricting 'obj' using a guard.
    """

    obj.a                       # only provided by instances of C
    if i:
        return obj.m(i)         # should use the method directly since obj is an instance
    else:
        return obj.m

def h(obj, fn):

    """
    Obtain an attribute on 'obj', performing an operation depending on 'fn'.
    This tests attribute access and invocation, restricting 'obj' using a guard
    on a re-assignment of the name.
    """

    if fn:
        obj = fn()
        obj.a                   # only provided by instances of C
        return obj.m(1)
    else:
        return obj.m

# Main program.

c = C()
d = D()

try:
    print f(C, 1)               # fails
except UnboundMethodInvocation:
    print "f(C, 1): Unbound method is not callable."

fn = f(C, 0)

try:
    print fn(2)                 # fails
except UnboundMethodInvocation:
    print "fn(2): Unbound method is not callable."

print get_using(fn, c)(2)       # 2
print get_using(f(C, 0), c)(2)  # 2

try:
    print g(C, 1)               # should fail with an error caused by a guard
except TypeError:
    print "g(C, 1): C is not a suitable argument."

print g(c, 1)                   # 1
print g(c, 0)(3)                # 3

print h(c, getc)                # 1
print h(c, 0)(4)                # 4

try:
    print h(c, getd)            # should fail with an error caused by a guard
except TypeError:
    print "h(c, getd): getd provides an unsuitable result."

try:
    print h(d, 0)(4)            # should fail with an error caused by a test
except TypeError:
    print "h(d, 0): d is not a suitable argument."

try:
    print g(c, 1)(5)
except TypeError:
    print "g(c, 1)(5): attempt to invoke an integer result from g."

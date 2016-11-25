class C:
    def __init__(self):
        self.a = 1
    def m(self, x):
        return x

class D:
    pass

def getc():
    return C()

def getd():
    return D()

def f(obj, i):
    if i:
        return obj.m(i)         # should cause access to an unbound method
    else:
        return obj.m

def g(obj, i):
    obj.a                       # only provided by instances of C
    if i:
        return obj.m(i)         # should use the method directly since obj is an instance
    else:
        return obj.m

def h(obj, fn):
    if fn:
        obj = fn()
        obj.a                   # only provided by instances of C
        return obj.m(1)
    else:
        return obj.m

c = C()

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

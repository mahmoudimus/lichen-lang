class C:
    def c(self):
        return 1

class D(C):
    def d(self):
        return 3

a = 4
l = []

def f(x):

    # Test global mutation.

    l.append(x.c())

    # Test function initialisation.

    def g(y, x=x): # x must be introduced as default here
        if y:
            x = D()
        return x.d(), y, a # UnboundLocalError in Python (if y is a false value)

    return g

# Provide a default instance for a function to be obtained.

fn = f(C())
print l                     # [1]
print fn                    # __main__.f.$l0
try:
    print fn(2)             # should fail due to g requiring an object providing d
except TypeError:
    print "fn(2): fn initialised with an inappropriate object"

try:
    print fn(0)             # should fail due to g requiring an object providing d
except TypeError:
    print "fn(0): fn initialised with an inappropriate object"

# Override the default when calling the function.

print fn(2, D())            # (3, 2, 4)
print fn(0, D())            # (3, 0, 4)

# Provide a more suitable default instance for the function.

fn = f(D())
print l                     # [1, 1]
print fn(2)                 # (3, 2, 4)
print fn(0)                 # (3, 0, 4)
print fn(0, D())            # (3, 0, 4)

# Override with an unsuitable object even though it would be ignored.

try:
    print fn(1, C())
except TypeError:
    print "fn(1, C()): an unsuitable argument was given."

# Override with an unsuitable object.

try:
    print fn(0, C())
except TypeError:
    print "fn(0, C()): an unsuitable argument was given."

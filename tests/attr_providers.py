class C:
    def __init__(self):
        self.a = 1
        self.c = 3

    b = 2

class D:
    def __init__(self):
        self.a = 3
        self.b = 4

class E:
    a = 5
    b = 6

def f(x):
    return x.a, x.b

def g(x):

    # Should only permit D instance and E.

    x.a = 7
    x.b = 8
    return f(x)

def h(x):
    x.c
    x.a = 4
    x.b
    return f(x)

c = C()
d = D()
e = E()

print f(c)          # (1, 2)
print f(d)          # (3, 4)
print f(e)          # (5, 6)
print f(E)          # (5, 6)

try:
    print g(c)      # should fail with an error caused by a test
except TypeError:
    print "g(c): c is not a suitable argument."

print g(d)          # (7, 8)

try:
    print g(e)      # should fail with an error caused by a test
except TypeError:
    print "g(e): e is not a suitable argument."

print g(E)          # (7, 8)

print h(c)          # (4, 5)

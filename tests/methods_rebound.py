class C:
    def f(self):
        print self
        return self.value()

    def value(self):
        return 123

c = C()

class D:
    f = c.f

d = D()

def fn():
    return 456

class E:
    f = fn
    g = C.f

e = E()

# Normal method access and invocation.

print c.f.__name__                  # f
print c.f()                         # <__main__.C instance>
                                    # 123

# Access and call assigned bound method.

print d.f.__name__                  # wrapper
print d.f()                         # <__main__.C instance>
                                    # 123

# Access and call assigned function.

print e.f.__name__                  # fn
print e.f()                         # 456

# Access details of assigned method.

print e.g.__name__                  # f

# Attempt to call method belonging to another class via an incompatible
# instance. In Python, this would be an unbound method call attempt.

try:
    print e.g()
except TypeError:
    print "e.g(): e is an incompatible instance for E.g which is C.f"

g = get_using(E.g, c)
print g.__name__                    # f
print g()                           # <__main__.C instance>
                                    # 123

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

print c.f.__name__                  # f
print c.f()                         # <__main__.C instance>
                                    # 123
print d.f.__name__                  # wrapper
print d.f()                         # <__main__.C instance>
                                    # 123

print e.f.__name__                  # fn
print e.f()                         # 456
print e.g.__name__                  # f

try:
    print e.g()
except TypeError:
    print "e.g(): e is an incompatible instance for E.g which is C.f"

g = get_using(E.g, c)
print g.__name__                    # f
print g()                           # <__main__.C instance>
                                    # 123

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

print c.f.__name__                  # f
print c.f()                         # <__main__.C instance>
                                    # 123
print d.f.__name__                  # wrapper
print d.f()                         # <__main__.C instance>
                                    # 123

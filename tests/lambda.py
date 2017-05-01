f = lambda x: (x, 1)

class C:
    f = lambda x: (x, 2)

print f(123)            # (123, 1)

c = C()
print c.f               # __main__.C.$l0
print c.f(123)          # (123, 2)

c.f = f
print c.f(123)          # (123, 1)

C.f = f
c2 = C()
print c2.f(123)         # (123, 1)

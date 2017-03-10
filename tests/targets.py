class C:
    def f(x):
        return x

    def g(a, b, c):
        return a

    def h(x):
        return x

c = C()
f = c.f
g = c.g
h = c.h

print g(h(12345), g(f(23456), h(34567), f(45678)), f(56789))

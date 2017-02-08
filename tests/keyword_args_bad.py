class C:
    def f(self, x, y, z):
        return z

class D:
    def f(self, a, b, c):
        return c

def pqr(obj):
    return obj.f(1, 2, r=3)     # no corresponding function

c = C()
d = D()

print pqr(c)                    # should fail

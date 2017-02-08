class C:
    def f(self, x, y, z):
        return z

class D:
    def f(self, a, b, c):
        return c

def xyz(obj):
    return obj.f(1, 2, z=3)

def abc(obj):
    return obj.f(4, 5, c=6)

c = C()
d = D()

print xyz(c)                    # 3
print abc(d)                    # 6

try:
    print xyz(d)                # should raise an exception
except TypeError:
    print "xyz(d): argument cannot be used"

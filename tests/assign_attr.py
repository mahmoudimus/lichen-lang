class C:
    def __init__(self, x):
        self.x = x

    def __str__(self):
        return "C(%r)" % self.x

    __repr__ = __str__

class D:
    x = 1

def f():
    return D

c = C(C(1)) # c.x.x = 1
print c     # C(C(1))
print c.x   # C(1)
print c.x.x # 1
c.x.x = 2
print c     # C(C(2))
print c.x   # C(2)
print c.x.x

print D.x   # 1
D.x = 2
print D.x   # 2
D.x = C(3)
print D.x   # C(3)
print D.x.x # 3
D.x.x = 4
print D.x.x # 4

f().x = 5
print D.x   # 5

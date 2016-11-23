class C:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def c(self):
        return self.x

class D(C):
    def d(self):
        return self.y

class E(D):
    def c(self):
        return self.z

c = C(1, 2, 3)
d = D(1, 2, 3)
e = E(1, 2, 3)

print c.c() # 1
print d.c() # 1
print e.c() # 3
print d.d() # 2
print e.d() # 2

class C:
    def __init__(.x, .y, .z, x): # no explicit self, attributes initialised
        pass

    def c():
        return self.x

class D(C):
    def d():
        return self.y

class E(D):
    def c():
        return self.z

c = C(1, 2, 3, 4)
d = D(1, 2, 3, 4)
e = E(1, 2, 3, 4)

print c.c() # 1
print d.c() # 1
print e.c() # 3
print d.d() # 2
print e.d() # 2

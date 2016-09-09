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

result1 = c.c() # 1
result2 = d.c() # 1
result3 = e.c() # 3
result4 = d.d() # 2
result5 = e.d() # 2

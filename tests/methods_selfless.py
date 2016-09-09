class C:
    def __init__(x, y, z): # no explicit self
        self.x = x
        self.y = y
        self.z = z

    def c():
        return self.x

class D(C):
    def d():
        return self.y

class E(D):
    def c():
        return self.z

c = C(1, 2, 3)
d = D(1, 2, 3)
e = E(1, 2, 3)

result1 = c.c() # 1
result2 = d.c() # 1
result3 = e.c() # 3
result4 = d.d() # 2
result5 = e.d() # 2

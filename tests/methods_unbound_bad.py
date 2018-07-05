class C:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def c(self):
        return self.x

c = C(1, 2, 3)
print c.c() # 1
print C.c() # bad

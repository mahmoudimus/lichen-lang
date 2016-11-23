class C:
    l = [2, 4, 6, 8, 10]
    s = "test"
    def __init__(self, x):
        self.x = x
        self.y = 3
        self.z = "zebra libre"

c = C([1])
x = c.x
f = c.x.__len__
print f() # 1

y = c.l
g = c.l.__len__
print g() # 5

yy = C.l
gg = C.l.__len__
print gg() # 5

z = c.s
h = c.s.__len__
print h() # 4

zz = C.s
hh = C.s.__len__
print hh() # 4

a = c.y
b = c.z
i = c.z.__len__
print i() # 11

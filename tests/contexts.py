class C:
    l = [2]
    s = "test"
    def __init__(self, x):
        self.x = x
        self.y = 3
        self.z = "z"

c = C([1])
x = c.x
f = c.x.__len__
result1 = f()

y = c.l
g = c.l.__len__
result2 = g()

yy = C.l
gg = C.l.__len__
result22 = gg()

z = c.s
h = c.s.__len__
result3 = h()

zz = C.s
hh = C.s.__len__
result33 = hh()

a = c.y
b = c.z
i = c.z.__len__
result4 = i()

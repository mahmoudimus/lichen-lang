class C:
    l = [2, 4, 6, 8, 10]
    s = "test"
    def __init__(self, x):
        self.x = x
        self.y = 3
        self.z = "zebra libre"
    def __len__(self):
        return len(self.z)

c = C([1])
x = c.x
f = c.x.__len__
print c             # <__main__.C instance>
print x             # [1]
print f             # __builtins__.list.list.__len__
print f()           # 1

y = c.l
g = c.l.__len__
print y             # [2, 4, 6, 8, 10]
print g             # __builtins__.list.list.__len__
print g()           # 5

yy = C.l
gg = C.l.__len__
print yy            # [2, 4, 6, 8, 10]
print gg            # __builtins__.list.list.__len__
print gg()          # 5

z = c.s
h = c.s.__len__
print z             # test
print h             # __builtins__.str.basestring.__len__
print h()           # 4

zz = C.s
hh = C.s.__len__
print zz            # test
print hh            # __builtins__.str.basestring.__len__
print hh()          # 4

a = c.y
b = c.z
i = c.z.__len__
print a             # 3
print b             # zebra libre
print i             # __builtins__.str.basestring.__len__
print i()           # 11

j = C.__len__
k = get_using(j, c)
try:
    print j()
except UnboundMethodInvocation:
    print "j(): invocation of method with class context"
print k()           # 11

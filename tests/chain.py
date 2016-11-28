class C:
    class D:
        class E:
            def m(self, x):
                self.x = x
                l = self.x.__len__
                s = self.o
                return self.o.__len__
            n = 123
            o = "123"

        p = "456"
        q = 789

        class F(E):
            def r(self, y):
                s = self.o
                C.D.F.t = 234
                return self.o.__len__
            t = 123
            def u(self):
                return self.o
            def v(self):
                return self.u().__len__

def static():
    c = C
    d = C.D
    e = C.D.E
    f = C.D.E.m
    g = C.D.E.n
    h = C.D.p

    print c                                 # __main__.C
    print d                                 # __main__.C.D
    print e                                 # __main__.C.D.E
    print f                                 # __main__.C.D.E.m
    print g                                 # 123
    print h                                 # "456"

def static_via_constant():
    i = C.D.p.__len__

    print i                                 # __builtins__.str.basestring.__len__

def assign():
    C.D.q = 987

def indirect():
    e = C.D.E
    inst = e()
    method = inst.m
    return method("5")

def broken():
    inst2 = C.D.F()
    l = inst2.u().__len__
    return l

static()
static_via_constant()
assign()
print indirect()                            # __builtins__.str.basestring.__len__
print indirect()()                          # 3
print broken()                              # __builtins__.str.basestring.__len__
print broken()()                            # 3

print C.D.q                                 # 987

# Static chains.

c = C
d = C.D
e = C.D.E
f = C.D.E.m
g = C.D.E.n
h = C.D.p

print c                                     # __main__.C
print d                                     # __main__.C.D
print e                                     # __main__.C.D.E
print f                                     # __main__.C.D.E.m
print g                                     # 123
print h                                     # "456"

# Static via constant.

i = C.D.p.__len__

print i                                     # __builtins__.str.basestring.__len__
print i()                                   # 3

# Static assignment.

C.D.q = 654

print C.D.q                                 # 654

# Indirect accesses.

inst = e()
method = inst.m
print method("5")                           # __builtins__.str.basestring.__len__
print method("5")()                         # 3

# Broken chains.

inst2 = C.D.F()
l = inst2.u().__len__
print l                                     # __builtins__.str.basestring.__len__
print l()                                   # 3

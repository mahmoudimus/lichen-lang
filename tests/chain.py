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

def static_via_constant():
    i = C.D.p.__len__

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

static()
static_via_constant()
assign()
result1 = indirect()
broken()

# Static chains.

c = C
d = C.D
e = C.D.E
f = C.D.E.m
g = C.D.E.n
h = C.D.p

# Static via constant.

i = C.D.p.__len__

# Static assignment.

C.D.q = 987

# Indirect accesses.

inst = e()
method = inst.m
result2 = method("5")

# Broken chains.

inst2 = C.D.F()
l = inst2.u().__len__

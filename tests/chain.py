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

def main():
    c = C
    d = C.D
    e = C.D.E
    f = C.D.E.m
    g = C.D.E.n
    h = C.D.p
    i = C.D.p.__len__
    C.D.q = 987
    inst = e()
    method = inst.m
    return method("5")

result1 = main()
c = C
d = C.D
e = C.D.E
f = C.D.E.m
g = C.D.E.n
h = C.D.p
i = C.D.p.__len__
C.D.q = 987
inst = e()
method = inst.m
result2 = method("5")

class C:
    class D:
        class E:
            def m(self, x):
                return x
            n = 123
        p = "456"

def main():
    c = C
    d = C.D
    e = C.D.E
    f = C.D.E.m
    g = C.D.E.n
    h = C.D.p
    i = C.D.p.__len__
    inst = e()
    method = inst.m
    return method(5)

result1 = main()
c = C
d = C.D
e = C.D.E
f = C.D.E.m
g = C.D.E.n
h = C.D.p
i = C.D.p.__len__
inst = e()
method = inst.m
result2 = method(5)

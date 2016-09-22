class C:
    class D:
        class E:
            def m(self, x):
                return x

def main():
    c = C
    d = C.D
    e = C.D.E
    f = C.D.E.m
    inst = e()
    method = inst.m
    return method(5)

result1 = main()
c = C
d = C.D
e = C.D.E
f = C.D.E.m
inst = e()
method = inst.m
result2 = method(5)

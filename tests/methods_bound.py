class C:
    def m(self, x):
        return x

def f(obj, i):
    if i:
        return obj.m(i)
    else:
        return obj.m

c = C()
result1 = f(c, 1)
fn = f(c, 0)
result2 = fn(2)

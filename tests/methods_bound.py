class C:
    def m(self, x):
        return x

def f(obj, i):
    if i:
        return obj.m(i)
    else:
        return obj.m

c = C()
print f(c, 1)    # 1
print f(c, 0)(2) # 2
fn = f(c, 0)
print fn(2)      # 2

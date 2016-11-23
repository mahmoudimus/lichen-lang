class C:
    def m(self, x):
        return x

def f(obj, i):
    if i:
        return obj.m(i)
    else:
        return obj.m

c = C()
#print f(C, 1)                 # NOTE: Need to raise and handle error.
fn = f(C, 0)
print get_using(fn, c)(2)      # 2
print get_using(f(C, 0), c)(2) # 2

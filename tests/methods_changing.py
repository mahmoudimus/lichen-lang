class C:
    def f(self):
        return 1

    def g(self):
        return self.f()

class D(C):
    pass

def f():
    return 2

c = C()
d = D()

# Invoke a method that calls the default version of f.

print c.g()                 # 1
print d.g()                 # 1

# Replace f in C and invoke the method again. For C, f will have changed,
# but for D, f will retain its original value.

C.f = f

print c.g()                 # 2
print d.g()                 # 1

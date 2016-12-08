class C:
    def f(self):
        return self.x

class D(C):
    pass

class E(C):
    def __init__(self, x):
        self.x = x

d = D()
print d.f()

e = E(2)
print e.f()

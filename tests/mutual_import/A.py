from B import C, g

class D(C):
    d = 3
    def m(self):
        return self.d

def f(x):
    return x.m()

def h(x):
    return g(x)

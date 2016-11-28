from A import D, f

class C:
    c = 1
    def m(self):
        return self.c

class E(D):
    e = 2
    def m(self):
        return self.e

def g(x):
    return f(x)

a = 4

def f(x):
    def g(y, x=x):
        def h(z, x=x, y=y):
            return x, y, z, a
        return h
    return g

result = f(1)(2)(3)
assert result == (1, 2, 3, 4)

a = 4

def f(x):
    def g(y):
        def h(z):
            return x, y, z, a
        return h
    return g

result = f(1)(2)(3)
assert result == (1, 2, 3, 4)

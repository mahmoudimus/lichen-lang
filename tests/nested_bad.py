def f(x):
    def g(y, x=x):
        while 1:
            def h(z, x=x, y=y):
                return x, y, z, a
            a = 4 # not available for h, available in Python
            return h
    return g

result = f(1)(2)(3)
assert result == (1, 2, 3, 4)

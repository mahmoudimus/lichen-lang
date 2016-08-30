a = 4

def f(x):
    def g(y):
        def h(y, z):
            return x, y, z, a # parameter y overrides outer scope
        return h
    return g

result = f(1)(2)(5, 3)
assert result == (1, 5, 3, 4)

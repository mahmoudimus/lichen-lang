a = 4

def f(x):
    if not x:
        def g(y):
            return x, y, a
    return g # UnboundLocalError: not defined if x is true

result = f(1)(2)
assert result == (1, 2, 4)

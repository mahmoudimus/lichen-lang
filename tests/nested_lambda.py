a = 4

def f(x):
    g = lambda y, x=x: lambda z, x=x, y=y: (x, y, z, a)
    return g

result = f(1)(2)(3)
assert result == (1, 2, 3, 4)

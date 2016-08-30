a = 4

def f(x):
    g = lambda y: lambda z: (x, y, z, a)
    return g

result = f(1)(2)(3)
assert result == (1, 2, 3, 4)

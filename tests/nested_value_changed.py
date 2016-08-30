a = 4

def f(x):
    def g():
        y = 2 # used to initialise h
        def h(z):
            return x, y, z, a
        y = 5 # Python uses this value directly from g in h
        return h
    return g

result = f(1)()(3)
assert result == (1, 2, 3, 4) # (1, 5, 3, 4) in Python

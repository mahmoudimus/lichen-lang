a = 4

def f(x):
    def g():
        def h(z):
            return x, y, z, a
        h(3)  # NameError in Python
        y = 2 # not available for h, detected during inspection
        return h
    return g

result = f(1)()(3)
assert result == (1, 2, 3, 4)

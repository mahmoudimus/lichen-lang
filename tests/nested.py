a = 4

def f(x):
    def g(y, x=x):
        def h(z, x=x, y=y):
            return x, y, z, a
        return h
    return g

fn = f(1)
print fn                        # __main__.f.$l0
print fn(2)                     # __main__.f.$l0.$l0
print fn(2)(3)                  # (1, 2, 3, 4)
print fn(2)(3, 5)               # (5, 2, 3, 4)
print fn(2)(3, 5, 6)            # (5, 6, 3, 4)

a = 4

def f(x):

    # Test function initialisation (f.$l0).

    def g(y, x=x):

        # Test function initialisation (f.$l0.$l0).

        def h(a, z, x=x, y=y):
            return x, y, z, a # parameter a overrides global scope

        return h

    return g

fn = f(1)
print fn                        # __main__.f.$l0
print fn(2)                     # __main__.f.$l0.$l0
print fn(2)(5, 3)               # (1, 2, 3, 5)
print fn(2)(5, 3, 6)            # (6, 2, 3, 5)
print fn(2)(5, 3, 6, 7)         # (6, 7, 3, 5)

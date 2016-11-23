a = 4

def f(x):
    def g(y, x=x):
        def h(a, z, x=x, y=y):
            return x, y, z, a # parameter a overrides global scope
        return h
    return g

result = f(1)(2)(5, 3)
print result[0]
print result[1]
print result[2]
print result[3]
assert result == (1, 2, 3, 5)

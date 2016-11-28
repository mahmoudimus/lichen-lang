a = 4

def f(x):
    #   f.$l0          f.$l0.$l0
    g = lambda y, x=x: lambda z, x=x, y=y: (x, y, z, a)
    return g

print f                 # __main__.f
print f(1)              # __main__.f.$l0
print f(1)(2)           # __main__.f.$l0.$l0

result = f(1)(2)(3)
print result[0]
print result[1]
print result[2]
print result[3]
print result            # (1, 2, 3, 4)

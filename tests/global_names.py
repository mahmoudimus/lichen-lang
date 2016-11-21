class C:
    x = 3

def f():
    x = g.x
    y = g
    return y.x

g = C
result = f()
print result

def f():
    l = [1, 2, 3]
    x = l
    a, b, c = l
    d, e, f = [1, 2, 3]
    print a, b, c           # 1, 2, 3
    print d, e, f           # 1, 2, 3
    print x                 # [1, 2, 3]

def g(x):
    l = [1, 2, 3]
    m = [4, l, 6]
    if x:
        n = l
    else:
        n = m
    print n

f()
g(0)                        # [4, [1, 2, 3], 6]
g(1)                        # [1, 2, 3]

l = [1, 2, 3]
x = l
a, b, c = l
d, e, f = [1, 2, 3]
print a, b, c               # 1, 2, 3
print d, e, f               # 1, 2, 3
print x                     # [1, 2, 3]
m = [4, l, 6]
if x:
    n = l
else:
    n = m
print n                     # [1, 2, 3]

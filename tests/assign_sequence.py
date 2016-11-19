def f():
    l = [1, 2, 3]
    x = l
    a, b, c = l
    d, e, f = [1, 2, 3]
    print a, b, c
    print d, e, f
    print x

def g(x):
    l = [1, 2, 3]
    m = [4, l, 6]
    if x:
        n = l
    else:
        n = m
    print n

f()
g(0)
g(1)

l = [1, 2, 3]
x = l
a, b, c = l
d, e, f = [1, 2, 3]
print a, b, c
print d, e, f
print x
m = [4, l, 6]
if x:
    n = l
else:
    n = m
print n

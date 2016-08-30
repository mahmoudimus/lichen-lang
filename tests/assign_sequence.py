def f():
    l = [1, 2, 3]
    x = l
    a, b, c = l
    d, e, f = [1, 2, 3]

def g(x):
    l = [1, 2, 3]
    m = [4, l, 6]
    if x:
        n = l
    else:
        n = m

l = [1, 2, 3]
x = l
a, b, c = l
d, e, f = [1, 2, 3]
m = [4, l, 6]
if x:
    n = l
else:
    n = m

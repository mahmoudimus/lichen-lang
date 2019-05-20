def f(x):
    x + 10
    return x

a = 1.0
b = 2.0
c = 3.0
d = f(a * b)

print a * b + c     # 5.0
print d + c         # 5.0
print d             # 2.0

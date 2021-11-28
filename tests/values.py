class X:
    def __init__(self, a, b):
        self.a = a
        self.b = b

def f(a, x):
    x.a = 3                 # x.b
    print a                 # 2
    print x.a               # 3
    return a + x.a

def g(x):
    return x.a, x.b

x = X(2, 3)
y = f(x.a, x)
print y                     # 5
z = g(x)
print z                     # (3, 3)

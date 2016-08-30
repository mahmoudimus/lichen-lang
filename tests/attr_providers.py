class C:
    def __init__(self):
        self.a = 1

    b = 2

class D:
    def __init__(self):
        self.a = 3
        self.b = 4

class E:
    a = 5
    b = 6

def f(x):
    return x.a, x.b

c = C()
d = D()
e = E()

result1 = f(c) # (1, 2)
result2 = f(d) # (3, 4)
result3 = f(e) # (5, 6)

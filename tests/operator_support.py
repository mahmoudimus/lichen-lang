class A:
    def __init__(self, x):
        self.x = x
    def __sub__(self, other):
        return self.x - other.x

class B:
    def __init__(self, x):
        self.x = x
    def __rsub__(self, other):
        return other.x - self.x

class C:
    def __init__(self, x):
        self.x = x

a = A(10)
b = B(5)
c = C(3)

print a - b                         # 5
print c - b                         # -2
print a - c                         # 7

try:
    print b - c                     # should raise an exception
except TypeError:
    print "b - c: b and c do not respectively support the __sub__ and __rsub__ operations"

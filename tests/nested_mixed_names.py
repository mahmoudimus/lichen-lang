class C:
    def c(self):
        return 1

class D:
    def d(self):
        return 3

a = 4

def f(x):
    x.c()
    def g(y, x=x): # x must be introduced as default here
        if y:
            x = D()
        return x.d(), y, a # UnboundLocalError in Python (if y is a false value)
    return g

result = f(C())(2)
print result[0]
print result[1]
print result[2]
assert result == (3, 2, 4)

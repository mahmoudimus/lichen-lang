class C:
    def __init__(self):
        self.x = 123

    def f(self):
        return self.x

class D:
    pass

c = C()
f = C.f
fn = get_using(C.f, c)
print fn                            # __main__.C.f
print fn()                          # 123

fn = get_using(C.f, C)
print fn                            # __main__.C.f
try:
    print fn()                      # fails
except UnboundMethodInvocation:
    print "fn(): method is unbound"

try:
    print f()                       # fails
except UnboundMethodInvocation:
    print "f(): method is unbound"

d = D()
try:
    fn = get_using(C.f, d)
except TypeError:
    print "get_using(C.f, d): d is not compatible with C"

fn = get_using(c, C.f)
print fn                            # <__main__.C instance>
try:
    print fn()                      # fails
except TypeError:
    print "fn(): object is not callable"

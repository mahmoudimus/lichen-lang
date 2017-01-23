class C:
    def __init__(self):
        self.x = 123

    def f(self):
        print self
        return self.x

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

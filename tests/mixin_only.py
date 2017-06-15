class MixIn:
    def f(self):
        return self.g()
    def f2(self):
        return self.g2()

class Concrete(MixIn):
    def g(self):
        return 13579
    def g2(self):
        return 13579

class Cement(MixIn):
    def g2(self):
        return 24680

m = MixIn()

try:
    print m.f()
except TypeError:
    print "m.f: cannot obtain attribute"

c = Concrete()
print c.f()         # 13579

try:
    print m.f2()
except TypeError:
    print "m.f2: cannot obtain attribute"

c2 = Cement()
print c2.f2()       # 24680

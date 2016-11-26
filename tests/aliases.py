class C:
    def m(self):
        return 1

D = C # alias for C

print C                 # "<type>"
print D                 # "<type>"

class E:
    def m(self):
        return 2

F = E # alias for E

print E                 # "<type>"
print F                 # "<type>"

def f():
    c = C
    d = D       # C
    cm = C.m
    dm = D.m    # C.m

    print c             # "<type>"
    print d             # "<type>"
    print cm            # "<function>"
    print dm            # "<function>"

    c = E
    d = F       # E
    cm = E.m
    dm = F.m    # E.m

    print c             # "<type>"
    print d             # "<type>"
    print cm            # "<function>"
    print dm            # "<function>"

f()

Cm = C.m
Dm = D.m
Em = E.m
Fm = F.m

print Cm                # "<function>"
print Dm                # "<function>"
print Em                # "<function>"
print Fm                # "<function>"

def g():
    Cm = E.m
    Dm = F.m    # E.m

    print Cm            # "<function>"
    print Dm            # "<function>"

g()

def h():
    global Em, Fm
    Em = C.m
    Fm = D.m    # C.m

    print Cm            # "<function>"
    print Dm            # "<function>"

h()

Ci = C()
Ei = E()

print Ci                # "__main__.C"
print Ei                # "__main__.E"

def i():
    c = Ci
    print c             # "__main__.C"
    c = Ei
    print c             # "__main__.E"

i()

def j():
    global Ei
    Ei = C()
    print Ei            # "__main__.C"

j()

L = []
M = [1]

print L                 # []
print M                 # [1]

def k():
    c = L
    print c             # []

k()

def l():
    global M
    M = []
    print M             # []

l()
print M                 # []

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
    print cm            # "__main__.C.m"
    print dm            # "__main__.C.m"

    c = E
    d = F       # E
    cm = E.m
    dm = F.m    # E.m

    print c             # "<type>"
    print d             # "<type>"
    print cm            # "__main__.E.m"
    print dm            # "__main__.E.m"

f()

Cm = C.m
Dm = D.m
Em = E.m
Fm = F.m

print Cm                # "__main__.C.m"
print Dm                # "__main__.C.m"
print Em                # "__main__.E.m"
print Fm                # "__main__.E.m"

def g():
    Cm = E.m
    Dm = F.m    # E.m

    print Cm            # "__main__.E.m"
    print Dm            # "__main__.E.m"

g()

def h():
    global Em, Fm
    Em = C.m
    Fm = D.m    # C.m

    print Em            # "__main__.C.m"
    print Fm            # "__main__.C.m"

h()

print Em            	# "__main__.C.m"
print Fm            	# "__main__.C.m"

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

print Ei            	# "__main__.C"

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

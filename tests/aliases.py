class C:
    def m(self):
        return 1

D = C # alias for C

class E:
    def m(self):
        return 2

F = E # alias for E

def f():
    c = C
    d = D       # C
    cm = C.m
    dm = D.m    # C.m

    c = E
    d = F       # E
    cm = E.m
    dm = F.m    # E.m

Cm = C.m
Dm = D.m
Em = E.m
Fm = F.m

def g():
    Cm = E.m
    Dm = F.m    # E.m

def h():
    global Em, Fm
    Em = C.m
    Fm = D.m    # C.m

Ci = C()
Ei = E()

def i():
    c = Ci
    c = Ei

def j():
    global Ei
    Ei = C()

L = []
M = [1]

def k():
    c = L

def l():
    global M
    M = []

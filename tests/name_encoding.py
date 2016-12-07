class C:
    def f(self):
        return 1

def C_f():
    return 2

def C__f():
    return 3

c = C()
print c.f()
print C_f()
print C__f()

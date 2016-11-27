class C:
    a = 1
    b = 2

class D(C):
    pass

def f():
    C.a = 3     # only changes C.a, not D.a

print C.a       # 1
print D.a       # 1
print C.b       # 2
print D.b       # 2

f()

print C.a       # 3
print D.a       # 1

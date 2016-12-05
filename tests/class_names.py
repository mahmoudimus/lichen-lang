class C:
    pass

def c():
    return 456

def f():
    return C()

print f()                       # 123

C = c

print f()                       # 456

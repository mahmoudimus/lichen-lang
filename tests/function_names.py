def f():
    return 123

def g():
    return 456

def h():
    return f()

print h()                           # 123

f = g

print h()                           # 456

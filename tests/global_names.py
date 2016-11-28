class C:
    x = 3

def f():
    x = g.x
    print x             # 3
    y = g
    print y             # __main__.C
    return y.x

def i():
    x = h.x
    y = h
    return y

g = C
result = f()
print result            # 3

h = C
print i()               # __main__.C
print i().x             # 3

h = C()
print i()               # <__main__.C instance>
print i().x             # 3

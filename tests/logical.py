def f(a, b, c):
    return a and b and c

def g(a, b, c):
    return a or b or c

def h(a, b, c):
    return a and b or c

def i(a, b, c):
    return a or b and c

def j(a, b, c):
    return f(a, b, c) and g(a, b, c) or c

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

print f(0, 0, 0)            # 0
print f(1, 0, 1)            # 0
print f(1, 1, 1)            # 1

print g(0, 0, 0)            # 0
print g(1, 0, 0)            # 1
print g(0, 0, 1)            # 1

print h(0, 0, 0)            # 0
print h(0, 0, 1)            # 1
print h(1, 0, 0)            # 0

print i(0, 0, 0)            # 0
print i(0, 0, 1)            # 0
print i(1, 0, 0)            # 1

print j(0, 0, 0)            # 0
print j(0, 0, 1)            # 1
print j(1, 0, 0)            # 0

# Test any and all functions.

l = [0, 0, 1, 0, 0]
print any(l)                # True
print all(l)                # False

l = [1, 1, "one", 1]
print any(l)                # True
print all(l)                # True

l = [1, 1, "one", ""]
print any(l)                # True
print all(l)                # False

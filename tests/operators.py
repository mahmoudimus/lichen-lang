import operator

def f(a, op, b):
    return op(a, b)

print f(1, operator.add, 2) # 3
print f(1, operator.sub, 2) # -1

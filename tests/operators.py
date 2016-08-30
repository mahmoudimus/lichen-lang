import operator

def f(a, op, b):
    return op(a, b)

f(1, operator.add, 2)
f(1, operator.sub, 2)

# Test attribute accesses with sequence assignments.

class C:
    a = 1; b = 2; c = 3

# This cannot assign directly...

print C.a, C.b, C.c                     # 1 2 3
C.a, C.b, C.c = C.c, C.b, C.a
print C.a, C.b, C.c                     # 3 2 1

# This cannot assign directly...

D = C
C.a, C.b, C.c = D.c, D.b, D.a
print C.a, C.b, C.c                     # 1 2 3

# Test name accesses with sequence assignments.

a = 1; b = 2; c = 3

# This cannot assign directly...

print a, b, c                           # 1 2 3
a, b, c = c, b, a
print a, b, c                           # 3 2 1

# This can assign directly...

d, e, f = c, b, a
print d, e, f                           # 1 2 3

# This can assign directly...

a, (b, c) = d, (e, f)
print a, b, c                           # 1 2 3

# This cannot assign directly...

(c, b), a = (a, b), c
print a, b, c                           # 3 2 1

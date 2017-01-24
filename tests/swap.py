class C:
    a = 1; b = 2; c = 3

print C.a, C.b, C.c                     # 1 2 3
C.a, C.b, C.c = C.c, C.b, C.a
print C.a, C.b, C.c                     # 3 2 1

D = C
C.a, C.b, C.c = D.c, D.b, D.a
print C.a, C.b, C.c                     # 1 2 3

import A

print A                 # A
print A.C               # B.C
print A.C()             # <B.C instance>
print A.h               # A.h

print A.h(A.C())        # 1
print A.h(A.D())        # 3

from B import E

print A.h(E())          # 2

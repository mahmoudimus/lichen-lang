print isinstance("string", str)     # True
print isinstance("string", int)     # False
print isinstance(123, int)          # True
print isinstance(123, str)          # False
print

class A:
    pass

class B(A):
    pass

class C(B):
    pass

a = A()
b = B()
c = C()

print isinstance(a, A)              # True
print isinstance(b, B)              # True
print isinstance(c, C)              # True
print
print isinstance(a, a)              # False
print isinstance(b, b)              # False
print isinstance(c, c)              # False
print
print isinstance(A, a)              # False
print isinstance(B, b)              # False
print isinstance(C, c)              # False
print
print isinstance(a, B)              # False
print isinstance(b, C)              # False
print isinstance(c, A)              # True
print
print isinstance(a, C)              # False
print isinstance(b, A)              # True
print isinstance(c, B)              # True
print
print issubclass(A, A)              # True
print issubclass(B, B)              # True
print issubclass(C, C)              # True
print
print issubclass(a, a)              # False
print issubclass(b, b)              # False
print issubclass(c, c)              # False
print
print issubclass(a, A)              # False
print issubclass(b, B)              # False
print issubclass(c, C)              # False
print
print issubclass(A, B)              # False
print issubclass(B, C)              # False
print issubclass(C, A)              # True
print
print issubclass(A, C)              # False
print issubclass(B, A)              # True
print issubclass(C, B)              # True

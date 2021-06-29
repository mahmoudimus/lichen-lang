i = int(123)
j = 123
print i, j, i == j      # 123 123 True
k = 456
print i, k, i == k      # 123 456 False
h = int(789)
print i, h, i == h      # 123 789 False
print j, h, j == h      # 123 789 False

try:
    a = int("a")        # should raise an exception
except ValueError, exc:
    print 'int("a") failed:', exc.value

try:
    a = int("!")        # should raise an exception
except ValueError, exc:
    print 'int("!") failed:', exc.value

a = int("a", 16)
b = int("123")
print a                 # 10
print b, i, b == i      # 123, 123, True
print b, j, b == j      # 123, 123, True

a_is_int = isinstance(a, int)
j_is_int = isinstance(j, int)

print a_is_int          # True
print j_is_int          # True

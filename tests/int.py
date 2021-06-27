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

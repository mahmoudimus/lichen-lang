l = range(0, 10)
print l                         # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print len(l)                    # 10

x = xrange(0, -10, -2)
print x                         # __builtins__.span.xrange(0, -10, -2)
print len(x)                    # 5

for i in x:
    print i                     # 0
                                # -2
                                # -4
                                # -6
                                # -8

x = xrange(0, -10, 2)
print x                         # __builtins__.span.xrange(0, 0, 2)
print len(x)                    # 0

y = xrange(4, 8)
print y                         # __builtins__.span.xrange(4, 8, 1)
print enumerate(y)              # [(0, 4), (1, 5), (2, 6), (3, 7)]
print sum(y)                    # 22
print map(lambda x: x*2, y)     # [8, 10, 12, 14]
print filter(lambda x: x%2, y)  # [5, 7]
print max(y)                    # 7
print min(y)                    # 4

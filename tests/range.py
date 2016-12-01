l = range(0, 10)
print l                     # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print len(l)                # 10

x = xrange(0, -10, -2)
print x                     # __builtins__.span.xrange(0, -10, -2)
print len(x)                # 5

for i in x:
    print i                 # 0
                            # -2
                            # -4
                            # -6
                            # -8

x = xrange(0, -10, 2)
print x                     # __builtins__.span.xrange(0, 0, 2)
print len(x)                # 0

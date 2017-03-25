# Obtain a list computed by range.

l = range(0, 10)
print l                                     # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print len(l)                                # 10

# Test a descending xrange.

x = xrange(0, -10, -2)
print x                                     # __builtins__.span.xrange(0, -10, -2)
print len(x)                                # 5

for i in x:
    print i                                 # 0
                                            # -2
                                            # -4
                                            # -6
                                            # -8

# Test an empty xrange.

x = xrange(0, -10, 2)
print x                                     # __builtins__.span.xrange(0, 0, 2)
print len(x)                                # 0

# Test a simple ascending xrange.

y = xrange(4, 8)
print y                                     # __builtins__.span.xrange(4, 8, 1)

# Test enumerate and sum.

print enumerate(y)                          # [(0, 4), (1, 5), (2, 6), (3, 7)]
print sum(y)                                # 22

# Test map and filter using lambdas.

print map(lambda x: x*2, y)                 # [8, 10, 12, 14]
print filter(lambda x: x%2, y)              # [5, 7]

# Test the limits of the range.

print max(y)                                # 7
print min(y)                                # 4

# Reproduce the sum function using reduce and a lambda.

print reduce(lambda x, y: x+y, y)           # 22
print reduce(lambda x, y: x+y, y, 0)        # 22

# Test a single element range.

single = xrange(3, 5, 2)
print list(single)                          # [3]
print reduce(lambda x, y: x+y, single)      # [3]

# Test a double element range.

double = xrange(3, 5, 1)
print list(double)                          # [3, 4]
print reduce(lambda x, y: x+y, double)      # [7]

# Test steps not coinciding with the end.

beyond = xrange(4, 9, 2)
print list(beyond)                          # [4, 6, 8]
print len(beyond)                           # 3

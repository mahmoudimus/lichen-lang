l = [1, 2, 3]

# Test else clause.

for i in l:
    print i             # 1
                        # 2
                        # 3
else:
    print 4             # 4

# Test break versus else clause.

for i in l:
    print i             # 1
                        # 2
    if i == 2:
        break
else:
    print 3

# Test StopIteration in loop.

try:
    for i in l:
        print i         # 1
                        # 2
        if i == 2:
            raise StopIteration
    else:
        print 3

except StopIteration:
    print "stopped"     # stopped

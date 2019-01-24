l = [1, 2, 3]

for i in l:
    print i             # 1
                        # 2
                        # 3
else:
    print 4             # 4

for i in l:
    print i             # 1
                        # 2
    if i == 2:
        break
else:
    print 3

l = range(0, 10)
print l                     # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

s = slice(2, 5)
print s                     # __builtins__.span.slice(2, 5, 1)

print l[s]                  # [2, 3, 4]
print l[2:5]                # [2, 3, 4]
print l[2:5:-1]             # []
print l[5:2:-1]             # [5, 4, 3]
print l[1:9:2]              # [1, 3, 5, 7]
print l[9:1:-2]             # [9, 7, 5, 3]
print l[::-1]               # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

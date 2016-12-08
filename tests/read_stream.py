from sys import stdin

print "Reading 10 bytes..."
s = stdin.read(10)
print s

print "Reading to end of file..."
s = stdin.read()
print s

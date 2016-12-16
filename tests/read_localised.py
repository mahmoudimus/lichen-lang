from sys import lstdin

print lstdin
print lstdin.encoding
print "Reading 10 bytes..."
s = lstdin.read(10)
print s

print "Reading to end of file..."
s = lstdin.read()
print s

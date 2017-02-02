from sys import lstdin

print lstdin                        # <libc.io.sysstream instance>
print lstdin.encoding               # ISO-8859-15
print "Reading 10 bytes..."
s = lstdin.read(10)
print s

print "Reading to end of file..."
s = lstdin.read()
print s

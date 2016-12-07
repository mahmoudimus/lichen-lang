from posix import read

try:
    s = read(3, 10)
except IOError, exc:
    print "read(3, 10): input/output error condition", exc.value

s = read(0, 10)
print s

try:
    f = open("tests/read_file.py")  # this file!
except IOError, exc:
    print "I/O error occurred:", exc.value
    raise

try:
    s = f.read(5)
    print s                         # try:
    s = f.read(49)
    print s                         #     f = open("tests/read_file.py")   # this file!
    s = f.read()
    print s
finally:
    f.close()

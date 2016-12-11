s = "Hello"
s += " world!"
print s                     # Hello world!
print len(s)                # 12

s2 = "Hello worlds!"
print s2                    # Hello worlds!
print len(s2)               # 13
print s < s2                # True
print s <= s2               # True
print s == s2               # False
print s != s2               # True
print s >= s2               # False
print s > s2                # False

print s[0]                  # H
print s[-1]                 # !

print ord(s[0])             # 72

try:
    print ord(s)            # should raise an exception
except ValueError, exc:
    print "ord(s): value is not appropriate", exc.value

l = ["Hello", "world!"]
s3 = " ".join(l)
print s3                    # Hello world!
print len(s3)               # 12

s4 = "".join(l)
print s4                    # Helloworld!
print len(s4)               # 11

s5 = "--".join(l)
print s5                    # Hello--world!
print len(s5)               # 13

print hash(s)
print hash(s2)
print hash(s3)
print hash(s4)
print hash(s5)

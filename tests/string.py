s = "Hello"
s += " world!"
print s                     # Hello world!

s2 = "Hello worlds!"
print s2                    # Hello worlds!
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

s4 = "".join(l)
print s4                    # Helloworld!

print hash(s)
print hash(s2)
print hash(s3)
print hash(s4)

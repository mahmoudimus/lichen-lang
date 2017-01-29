s = "Hello"
s += " world!"
print s                     # Hello world!
print len(s)                # 12
print s[:5]                 # Hello
print s[5:]                 #  world!
print s[1:10:2]             # el ol
print s[10:1:-2]            # drwol
print s.find("w")           # 6
print s.find("w", 7)        # -1
print s.find("w", 0, 6)     # -1
print s.index("o")          # 4
print s.rfind("o")          # 7
print s.rfind("o", 7)       # 7
print s.rfind("o", 8)       # -1
print s.rfind("o", 0, 7)    # 4

try:
    print s.index("p")      # should raise an exception
except ValueError, exc:
    print 's.index("p"): value is not appropriate', exc.value

print s.startswith("Hello") # True
print s.startswith("world") # False
print s.endswith("world!")  # True
print s.endswith("Hello")   # False

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

print "# hash(s):",
print hash(s)
print "# hash(s2):",
print hash(s2)
print "# hash(s3):",
print hash(s3)
print "# hash(s4):",
print hash(s4)
print "# hash(s5):",
print hash(s5)

# Test multiplication of strings.

s6 = "abc"
print s6 * -1               #
print s6 * 0                #
print s6 * 1                # abc
print s6 * 2                # abcabc
print -1 * s6               #
print 0 * s6                #
print 1 * s6                # abc
print 2 * s6                # abcabc

# Test splitting of strings.

s7 = "Hello...\n  world,\n  planet,\n  globe."
print s7.split()            # ["Hello...", "world,", "planet,", "globe."]
print s7.split(maxsplit=2)  # ["Hello...", "world,", "planet,\n  globe."]
print s7.split("\n")        # ["Hello...", "  world,", "  planet,", "  globe."]

# NOTE: To test rsplit once list.insert is implemented.

# Test stripping of strings.

s8 = "  \nHello world\n  "
print repr(s8.strip())      # "Hello world"
print repr(s8.lstrip())     # "Hello world\n  "
print repr(s8.rstrip())     # "  \nHello world"

s9 = "xyzHello worldXYZ"
print repr(s9.strip("xyYZ"))    # "zHello worldX"
print repr(s9.lstrip("xyYZ"))   # "zHello worldXYZ"
print repr(s9.rstrip("xyYZ"))   # "xyzHello worldX"

# -*- coding: ISO-8859-1 -*-

import sys

# Print bytes.

s = b"���"
print s                             # ���
print len(s)                        # 3

# Obtain text and print it.

# Explicitly from bytes.

u = unicode("���", "ISO-8859-1")
print u                             # ���
print u.__class__                   # __builtins__.unicode.utf8string
print u.encode("ISO-8859-1")        # ���
print u.encoding                    # ISO-8859-1
print len(u)                        # 3

# Explicitly from Unicode literals.

u2 = u"���"
print u2                            # ���
print u2.__class__                  # __builtins__.unicode.utf8string
print u2.encode("ISO-8859-1")       # ���
print u2.encoding                   # ISO-8859-1
print len(u2)                       # 3

# Implicitly from string literals.

u3 = "���"
print u3                            # ���
print u3.__class__                  # __builtins__.unicode.utf8string
print u3.encode("ISO-8859-1")       # ���
print u3.encoding                   # ISO-8859-1
print len(u3)                       # 3

# Test invalid sequences.

try:
    u4 = unicode(s, "UTF-8")
except UnicodeDecodeError, exc:
    print "Attempt to decode", s, "as UTF-8 failed."

# Combine bytes and text.
# The text should be decoded.

su = s + u
print su                            # ������
print su.__class__                  # __builtins__.str.string
print len(su)                       # 6

# Combine text and bytes.
# The text should be decoded.

us = u + s
print us                            # ������
print us.__class__                  # __builtins__.str.string
print len(us)                       # 6

# Combine text and text.

uu2 = u + u2
print uu2                           # ������
print uu2.__class__                 # __builtins__.unicode.utf8string
print uu2.encoding                  # ISO-8859-1
print len(uu2)                      # 6

# Inspect and update the encoding of stdout.
# Note that su and us are byte strings and are not recoded.

print sys.stdout                    # <posix.io.sysstream instance>
print sys.stdout.encoding           # None

sys.stdout.encoding = "ISO-8859-1"
print sys.stdout.encoding           # ISO-8859-1
print u                             # ���
print su                            # ������
print us                            # ������

sys.stdout.encoding = "UTF-8"
print sys.stdout.encoding           # UTF-8
print u                             # æøå
print su                            # ������
print us                            # ������

# Reset the encoding.

sys.stdout.encoding = "ISO-8859-1"

# Test character access.

u0 = u[0]
print u0.__class__                  # __builtins__.unicode.utf8string
print u0.encoding                   # ISO-8859-1
print u0                            # �
print u[-1]                         # �
print len(u[0])                     # 1
print len(u[-1])                    # 1
print u[:2]                         # ��
print len(u[:2])                    # 2
print u[-1::-1]                     # ���
print len(u[-1::-1])                # 3

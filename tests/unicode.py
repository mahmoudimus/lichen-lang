# -*- coding: ISO-8859-1 -*-

import sys

# Print bytes.

s = b"���"
print s                             # ���

# Obtain text and print it.

# Explicitly from bytes.

u = unicode(s, "ISO-8859-1")
print u                             # æøå
print u.encode("ISO-8859-1")        # ���

# Explicitly from Unicode literals.

u2 = u"���"
print u2                            # æøå
print u2.encode("ISO-8859-1")       # ���

# Implicitly from string literals.

#u3 = "���"
#print u3                            # æøå
#print u3.encode("ISO-8859-1")       # ���

# Inspect and update the encoding of stdout.

print sys.stdout.encoding           # None
sys.stdout.encoding = "ISO-8859-1"
print u                             # ���

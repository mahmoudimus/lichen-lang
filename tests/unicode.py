# -*- coding: ISO-8859-1 -*-

import sys

# Print bytes.

s = "���"
print s                             # ���

# Obtain text and print it.

u = unicode(s, "ISO-8859-1")
print u                             # æøå
print u.encode("ISO-8859-1")        # ���

# Inspect and update the encoding of stdout.

print sys.stdout.encoding           # None
sys.stdout.encoding = "ISO-8859-1"
print u                             # ���

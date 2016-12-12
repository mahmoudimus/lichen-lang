# -*- coding: ISO-8859-1 -*-

import sys

# Print bytes.

s = "æøå"
print s                             # æøå

# Obtain text and print it.

u = unicode(s, "ISO-8859-1")
print u                             # Ã¦Ã¸Ã¥
print u.encode("ISO-8859-1")        # æøå

# Inspect and update the encoding of stdout.

print sys.stdout.encoding           # None
sys.stdout.encoding = "ISO-8859-1"
print u                             # æøå

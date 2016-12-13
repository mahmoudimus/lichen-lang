# -*- coding: ISO-8859-1 -*-

import sys

# Print bytes.

s = b"ÆØÅ"
print s                             # ÆØÅ

# Obtain text and print it.

# Explicitly from bytes.

u = unicode("æøå", "ISO-8859-1")
print u                             # Ã¦Ã¸Ã¥
print u.encode("ISO-8859-1")        # æøå

# Explicitly from Unicode literals.

u2 = u"æøå"
print u2                            # Ã¦Ã¸Ã¥
print u2.encode("ISO-8859-1")       # æøå

# Implicitly from string literals.

#u3 = "æøå"
#print u3                            # Ã¦Ã¸Ã¥
#print u3.encode("ISO-8859-1")       # æøå

# Combine bytes and text.
# The text should be decoded.

su = s + u
print su                            # ÆØÅæøå

# Combine text and bytes.
# The text should be decoded.

us = u + s
print us                            # æøåÆØÅ

# Inspect and update the encoding of stdout.

print sys.stdout.encoding           # None
sys.stdout.encoding = "ISO-8859-1"
print u                             # æøå
print su                            # ÆØÅæøå
print us                            # æøåÆØÅ

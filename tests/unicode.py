# -*- coding: ISO-8859-1 -*-

import sys

# Print bytes.

s = b"ÆØÅ"
print s                             # ÆØÅ
print len(s)                        # 3

# Obtain text and print it.

# Explicitly from bytes.

u = unicode("æøå", "ISO-8859-1")
print u                             # Ã¦Ã¸Ã¥
print u.__class__                   # __builtins__.unicode.utf8string
print u.encode("ISO-8859-1")        # æøå
print u.encoding                    # ISO-8859-1
print len(u)                        # 3

# Explicitly from Unicode literals.

u2 = u"æøå"
print u2                            # Ã¦Ã¸Ã¥
print u2.__class__                  # __builtins__.unicode.utf8string
print u2.encode("ISO-8859-1")       # æøå
print u2.encoding                   # ISO-8859-1
print len(u2)                       # 3

# Implicitly from string literals.

u3 = "æøå"
print u3                            # Ã¦Ã¸Ã¥
print u3.__class__                  # __builtins__.unicode.utf8string
print u3.encode("ISO-8859-1")       # æøå
print u3.encoding                   # ISO-8859-1
print len(u3)                       # 3

# Combine bytes and text.
# The text should be decoded.

su = s + u
print su                            # ÆØÅæøå
print su.__class__                  # __builtins__.str.string
print len(su)                       # 6

# Combine text and bytes.
# The text should be decoded.

us = u + s
print us                            # æøåÆØÅ
print us.__class__                  # __builtins__.str.string
print len(us)                       # 6

# Combine text and text.

uu2 = u + u2
print uu2                           # Ã¦Ã¸Ã¥
print uu2.__class__                 # __builtins__.unicode.utf8string
print uu2.encoding                  # ISO-8859-1
print len(uu2)                      # 6

# Inspect and update the encoding of stdout.
# Note that su and us are byte strings and are not recoded.

print sys.stdout.encoding           # None

sys.stdout.encoding = "ISO-8859-1"
print sys.stdout.encoding           # ISO-8859-1
print u                             # æøå
print su                            # ÆØÅæøå
print us                            # æøåÆØÅ

sys.stdout.encoding = "UTF-8"
print sys.stdout.encoding           # UTF-8
print u                             # Ã¦Ã¸Ã¥
print su                            # ÆØÅæøå
print us                            # æøåÆØÅ

# -*- coding: ISO-8859-15 -*-

import sys

# Print bytes.

s = b"ÆØÅ"
print "ISO-8859-15 values:"
print s                             # ÆØÅ
print len(s)                        # 3

s2 = b"\xe6\xf8\xe5"
print "ISO-8859-15 values:"
print s2                            # æøå
print s2.__class__                  # __builtins__.str.string
print len(s2)                       # 3

s3 = "\xe6\xf8\xe5"
print "ISO-8859-15 values:"
print s3                            # æøå
print s3.__class__                  # __builtins__.str.string
print len(s3)                       # 3

s4 = b"\u00e6\u00f8\u00e5"
print "Untranslated values:"
print s4                            # \u00e6\u00f8\u00e5
print s4.__class__                  # __builtins__.str.string
print len(s4)                       # 18

s5 = b"\346\370\345"
print "ISO-8859-15 values:"
print s5                            # æøå
print s5.__class__                  # __builtins__.str.string
print len(s5)                       # 3

s6 = "\346\370\345"
print "ISO-8859-15 values:"
print s6                            # æøå
print s6.__class__                  # __builtins__.str.string
print len(s6)                       # 3

s7 = r"\346\370\345"
print "Untranslated values:"
print s7                            # \346\370\345
print s7.__class__                  # __builtins__.unicode.utf8string
print len(s7)                       # 12

# Obtain text and print it.

# Explicitly from bytes.

u = unicode(b"æøå", "ISO-8859-15")
print "Unicode values:"
print u                             # æøå
print u.__class__                   # __builtins__.unicode.utf8string
print u.encode("ISO-8859-15")       # æøå
print u.encoding                    # ISO-8859-15
print len(u)                        # 3

# Explicitly from Unicode literals.

u2 = u"æøå"
print "Unicode values:"
print u2                            # æøå
print u2.__class__                  # __builtins__.unicode.utf8string
print u2.encode("ISO-8859-15")      # æøå
print u2.encoding                   # ISO-8859-15
print len(u2)                       # 3

# Implicitly from string literals.

u3 = "æøå"
print "Unicode values:"
print u3                            # æøå
print u3.__class__                  # __builtins__.unicode.utf8string
print u3.encode("ISO-8859-15")      # æøå
print u3.encoding                   # ISO-8859-15
print len(u3)                       # 3

# Explicitly from implicitly-converted literal.

u4 = unicode("æøå", "ISO-8859-15")
print "Unicode values:"
print u4                            # æøå
print u4.__class__                  # __builtins__.unicode.utf8string
print u4.encode("ISO-8859-15")      # æøå
print u4.encoding                   # ISO-8859-15
print len(u4)                       # 3

# Test Unicode values.

u5 = "\u00e6\u00f8\u00e5"
print "Unicode values:"
print u5                            # æøå
print u5.__class__                  # __builtins__.unicode.ut8string
print len(u5)                       # 3

# Test some untranslated values.

u6 = "\\u00e6\\u00f8\\u00e5"
print "Untranslated values:"
print u6                            # \u00e6\u00f8\u00e5
print u6.__class__                  # __builtins__.unicode.ut8string
print len(u6)                       # 18

# Test Unicode values.

u7 = u"\346\370\345"
print "Unicode values:"
print u7                            # æøå
print u7.__class__                  # __builtins__.unicode.ut8string
print len(u7)                       # 3

# Test Unicode values.

u8 = ur"\346\370\345"
print "Untranslated values:"
print u8                            # \346\370\345
print u8.__class__                  # __builtins__.unicode.ut8string
print len(u8)                       # 12

# Test invalid sequences.

try:
    u9 = unicode(s, "UTF-8")
except UnicodeDecodeError, exc:
    print "Attempt to decode", s, "as UTF-8 failed."

# Combine bytes and text.
# The text should be decoded.

su = s + u
print "ISO-8859-15 values:"
print su                            # ÆØÅæøå
print su.__class__                  # __builtins__.str.string
print len(su)                       # 6

# Combine text and bytes.
# The text should be decoded.

us = u + s
print "ISO-8859-15 values:"
print us                            # æøåÆØÅ
print us.__class__                  # __builtins__.str.string
print len(us)                       # 6

# Combine text and text.

uu2 = u + u2
print "Unicode values:"
print uu2                           # æøåæøå
print uu2.__class__                 # __builtins__.unicode.utf8string
print uu2.encoding                  # ISO-8859-15
print len(uu2)                      # 6

# Inspect and update the encoding of stdout.
# Note that su and us are byte strings and are not recoded.

print sys.stdout                    # <libc.io.sysstream instance>
print sys.stdout.encoding           # None

sys.stdout.encoding = "ISO-8859-15"
print "ISO-8859-15 and Unicode values as ISO-8859-15:"
print sys.stdout.encoding           # ISO-8859-15
print u                             # æøå
print su                            # ÆØÅæøå
print us                            # æøåÆØÅ

sys.stdout.encoding = "UTF-8"
print "Unicode values as UTF-8:"
print sys.stdout.encoding           # UTF-8
print u                             # ÃŠÃžÃ¥
print "ISO-8859-15 values bypassing UTF-8 output encoding:"
print su                            # ÆØÅæøå
print us                            # æøåÆØÅ

# Reset the encoding.

sys.stdout.encoding = "ISO-8859-15"

# Test character access.

u0 = u[0]
print u0.__class__                  # __builtins__.unicode.utf8string
print u0.encoding                   # ISO-8859-15
print u0                            # æ
print u[-1]                         # å
print len(u[0])                     # 1
print len(u[-1])                    # 1
print u[:2]                         # æø
print len(u[:2])                    # 2
print u[-1::-1]                     # åøæ
print len(u[-1::-1])                # 3

# Test character values.

print ord(u[0])                     # 230

try:
    print ord(u)                    # should raise an exception
except ValueError, exc:
    print "ord(u): value is not appropriate", repr(exc.value)

euro = "€"
print euro                          # €
print repr(euro)                    # "\u20ac"
print ord(euro)                     # 8364
print "\u20ac"                      # €

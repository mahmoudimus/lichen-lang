# -*- coding: ISO-8859-1 -*-

from posix.iconv import Converter

only_utf8 = Converter("UTF-8", "UTF-8")
to_utf8 = Converter("ISO-8859-1", "UTF-8")
to_utf16 = Converter("ISO-8859-1", "UTF-16")
from_utf8 = Converter("UTF-8", "ISO-8859-1")
from_utf16 = Converter("UTF-16", "ISO-8859-1")

try:
    iso = b"æøå"
    print iso                           # æøå
    to_utf8.feed(iso)
    utf8 = str(to_utf8)
    print utf8                          # Ã¦Ã¸Ã¥
    from_utf8.feed(utf8)
    print str(from_utf8)                # æøå
    to_utf16.feed(iso)
    utf16 = str(to_utf16)
    print utf16                         # ...
    from_utf16.feed(utf16)
    print str(from_utf16)               # æøå

    # Convert UTF-8 to UTF-8.

    only_utf8.feed(utf8)
    utf8_2 = str(only_utf8)
    print utf8_2                        # Ã¦Ã¸Ã¥

    # Convert part of a UTF-16 sequence, then convert the remainder, then obtain
    # the result.

    first = utf16[:3]
    second = utf16[3:]

    from_utf16.reset()
    print "first:", first               # ...
    from_utf16.feed(first)              # should have handled an incomplete input
    print "second:", second             # ...
    from_utf16.feed(second)             # should have handled the complete input
    print str(from_utf16)               # æøå

    # Convert part of a UTF-8 sequence, then the remainder, then get the result.

    first = utf8[:3]
    second = utf8[3:]

    from_utf8.reset()
    print "first:", first               # Ã¦Ã
    from_utf8.feed(first)               # should have handled an incomplete input
    print "second:", second             # ¸Ã¥
    from_utf8.feed(second)              # should have handled the complete input
    print str(from_utf8)                # æøå

    # Attempt to convert ISO-8859-1 characters as if they were UTF-8.

    from_utf8.reset()

    try:
        from_utf8.feed(iso)             # should raise an exception
    except UnicodeDecodeError, exc:
        print "Not UTF-8 input:", exc.value
    except OSError, exc:
        print "OSError:", exc.value

    print str(from_utf8)                #

    # Attempt to convert ISO-8859-1 characters following some UTF-8 ones.

    to_utf8.reset()
    to_utf8.feed("ÆØÅ")
    utf8_2 = str(to_utf8)

    from_utf8.reset()

    try:
        from_utf8.feed(utf8_2 + iso)    # should raise an exception
    except UnicodeDecodeError, exc:
        print "Not UTF-8 input:", exc.value
    except OSError, exc:
        print "OSError:", exc.value

    print str(from_utf8)                #

finally:
    to_utf8.close()
    to_utf16.close()
    from_utf8.close()
    from_utf16.close()

try:
    Converter("horses", "giraffes")
except OSError, exc:
    print 'Converter("horses", "giraffes"): not valid encodings; error is', exc.value

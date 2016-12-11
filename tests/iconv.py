# -*- coding: ISO-8859-1 -*-

from posix.iconv import Converter, EINVAL, EILSEQ

to_utf8 = Converter("ISO-8859-1", "UTF-8")
to_utf16 = Converter("ISO-8859-1", "UTF-16")
from_utf8 = Converter("UTF-8", "ISO-8859-1")
from_utf16 = Converter("UTF-16", "ISO-8859-1")

try:
    iso = "æøå"
    print iso                           # æøå
    utf = to_utf8.convert(iso)
    print utf                           # Ã¦Ã¸Ã¥
    print from_utf8.convert(utf)        # æøå
    utf = to_utf16.convert(iso)
    print utf                           # ...
    try:
        print from_utf16.convert(utf)       # æøå
    except OSError, exc:
        if exc.value == EINVAL:
            print "Incomplete input", exc.arg
        elif exc.value == EILSEQ:
            print "Invalid input", exc.arg
        else:
            print exc.value, exc.arg
finally:
    to_utf8.close()
    to_utf16.close()
    from_utf8.close()
    from_utf16.close()

try:
    Converter("horses", "giraffes")
except OSError, exc:
    print 'Converter("horses", "giraffes"): not valid encodings; error is', exc.value

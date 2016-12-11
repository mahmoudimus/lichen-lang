import locale

print locale.getlocale()
print locale.initlocale()
print locale.getlocale()
print locale.setlocale(locale.LC_CTYPE, "en_GB.UTF-8")
print locale.getlocale()

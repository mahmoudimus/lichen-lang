#!/usr/bin/env python

from referencing import decode_reference, Reference

def show_test(v1, v2):
    print "%r %r %r" % (v1 == v2, v1, v2)

# Compare decoded and constructed references.

var1 = decode_reference("<var>")
var2 = Reference("<var>")
show_test(var1, var2)

# Compare with var with superfluous origin.

var3 = Reference("<var>", "whatever")
show_test(var1, var3)

# Compare with var and alias.

var4 = Reference("<var>", None, "attribute")
show_test(var1, var4)

# Compare with var with superfluous origin and alias.

var5 = Reference("<var>", "whatever", "attribute")
show_test(var1, var5)
show_test(var5.get_origin(), None)

# Compare vars with different aliases.

var6 = Reference("<var>", None, "other")
show_test(var4, var6)

# Check aliased var.

var7 = var1.alias("attribute")
show_test(var7, var4)

# Check class references, firstly with someclass being identified as a class.

cls1 = decode_reference("<class>", "someclass")
cls2 = Reference("<class>", "someclass")
show_test(cls1, cls2)

# Check aliasing of class references.

cls3 = cls1.alias("attribute")
cls4 = cls2.alias("other")
show_test(cls3, cls4)

# Check other class references.

cls5 = decode_reference("<class>:someclass")
cls6 = Reference("<class>", "someclass")
show_test(cls5, cls6)

# Check aliasing again.

cls7 = cls5.alias("attribute")
cls8 = cls6.alias("other")
show_test(cls7, cls8)

# Check instance references. These do not make sense without an origin.

inst1 = decode_reference("<instance>:someclass", "whatever")
inst2 = Reference("<instance>", "someclass")
show_test(inst1, inst2)

# Check instantiation.

inst3 = cls5.instance_of()
show_test(inst1, inst3)

# Check modules.

mod1 = decode_reference("somemodule")
mod2 = Reference("<module>", "somemodule")
show_test(mod1, mod2)

mod3 = decode_reference("<module>:somemodule")
show_test(mod1, mod3)

mod4 = decode_reference("<module>", "somemodule")
show_test(mod1, mod4)

# vim: tabstop=4 expandtab shiftwidth=4

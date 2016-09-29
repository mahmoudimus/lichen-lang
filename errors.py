#!/usr/bin/env python

"""
Error classes.

Copyright (C) 2007, 2008, 2009, 2010, 2011, 2012
              2014, 2016 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""

class ProcessingError(Exception):

    "A processing error."

    pass

class ProgramError(ProcessingError):

    "A general program processing error."

    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.message)

    def __str__(self):
        return self.message

class NodeProcessingError(ProcessingError):

    "A processing error associated with a particular program node."

    def __init__(self, message, unit_name=None, astnode=None):
        self.message = message
        self.unit_name = unit_name
        self.astnode = astnode

    def get_lineno(self, node):

        "Search for line number information associated with 'node'."

        if node is None:
            return None

        lineno = node.lineno
        if lineno is not None:
            return lineno
        else:
            for child in node.getChildNodes():
                lineno = self.get_lineno(child)
                if lineno is not None:
                    return lineno
        return None

    def __repr__(self):
        return "%s(%r, %r, %r)" % (self.__class__.__name__, self.message, self.unit_name, self.astnode)

    def __str__(self):
        lineno = self.get_lineno(self.astnode)
        return "Error in %s%s: %s" % (self.unit_name, lineno and (" at line %s" % lineno) or "", self.message)

class InspectError(NodeProcessingError):

    "An error during the module inspection process."

    pass

class DeduceError(NodeProcessingError):

    "An error during the deduction process."

    pass

class TranslateError(NodeProcessingError):

    "An error during the module translation process."

    pass

# vim: tabstop=4 expandtab shiftwidth=4

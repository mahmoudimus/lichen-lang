from pyparser import parser, pytokenizer, pygram, error
from pyparser import consts

def recode_to_utf8(bytes, encoding):
    text = bytes.decode(encoding)
    if not isinstance(text, unicode):
        raise error.SyntaxError("codec did not return a unicode object")
    recoded = text.encode("utf-8")
    return recoded

def _normalize_encoding(encoding):
    """returns normalized name for <encoding>

    see dist/src/Parser/tokenizer.c 'get_normal_name()'
    for implementation details / reference

    NOTE: for now, parser.suite() raises a MemoryError when
          a bad encoding is used. (SF bug #979739)
    """
    if encoding is None:
        return None
    # lower() + '_' / '-' conversion
    encoding = encoding.replace('_', '-').lower()
    if encoding == 'utf-8' or encoding.startswith('utf-8-'):
        return 'utf-8'
    for variant in ['latin-1', 'iso-latin-1', 'iso-8859-1']:
        if (encoding == variant or
            encoding.startswith(variant + '-')):
            return 'iso-8859-1'
    return encoding

def _check_for_encoding(s):
    eol = s.find('\n')
    if eol < 0:
        return _check_line_for_encoding(s)[0]
    enc, again = _check_line_for_encoding(s[:eol])
    if enc or not again:
        return enc
    eol2 = s.find('\n', eol + 1)
    if eol2 < 0:
        return _check_line_for_encoding(s[eol + 1:])[0]
    return _check_line_for_encoding(s[eol + 1:eol2])[0]


def _check_line_for_encoding(line):
    """returns the declared encoding or None"""
    i = 0
    for i in range(len(line)):
        if line[i] == '#':
            break
        if line[i] not in ' \t\014':
            return None, False  # Not a comment, don't read the second line.
    return pytokenizer.match_encoding_declaration(line[i:]), True


class CompileInfo(object):
    """Stores information about the source being compiled.

    * filename: The filename of the source.
    * mode: The parse mode to use. ('exec', 'eval', or 'single')
    * flags: Parser and compiler flags.
    * encoding: The source encoding.
    """

    def __init__(self, filename, mode="exec", flags=0):
        self.filename = filename
        self.mode = mode
        self.encoding = None
        self.flags = flags


_targets = {
'eval' : pygram.syms.eval_input,
'single' : pygram.syms.single_input,
'exec' : pygram.syms.file_input,
}

class PythonParser(parser.Parser):

    def __init__(self, grammar=pygram.python_grammar):
        parser.Parser.__init__(self, grammar)

    def parse_source(self, textsrc, compile_info):
        """Main entry point for parsing Python source.

        Everything from decoding the source to tokenizing to building the parse
        tree is handled here.
        """
        # Detect source encoding.
        enc = None
        if textsrc.startswith("\xEF\xBB\xBF"):
            textsrc = textsrc[3:]
            enc = 'utf-8'
            # If an encoding is explicitly given check that it is utf-8.
            decl_enc = _check_for_encoding(textsrc)
            if decl_enc and decl_enc != "utf-8":
                raise error.SyntaxError("UTF-8 BOM with %s coding cookie" % decl_enc,
                                        filename=compile_info.filename)
        elif compile_info.flags & consts.PyCF_SOURCE_IS_UTF8:
            enc = 'utf-8'
            if _check_for_encoding(textsrc) is not None:
                raise error.SyntaxError("coding declaration in unicode string",
                                        filename=compile_info.filename)
        else:
            enc = _normalize_encoding(_check_for_encoding(textsrc))
            if enc is not None and enc not in ('utf-8', 'iso-8859-1'):
                try:
                    textsrc = recode_to_utf8(textsrc, enc)
                except LookupError as e:
                    # if the codec is not found, LookupError is raised.
                    raise error.SyntaxError("Unknown encoding: %s" % enc,
                                            filename=compile_info.filename)
                # Transform unicode errors into SyntaxError
                except UnicodeDecodeError as e:
                    message = str(e)
                    raise error.SyntaxError(message)

        flags = compile_info.flags

        # The tokenizer is very picky about how it wants its input.
        source_lines = textsrc.splitlines(True)
        if source_lines and not source_lines[-1].endswith("\n"):
            source_lines[-1] += '\n'
        if textsrc and textsrc[-1] == "\n":
            flags &= ~consts.PyCF_DONT_IMPLY_DEDENT

        self.prepare(_targets[compile_info.mode])
        tp = 0
        try:
            try:
                # Note: we no longer pass the CO_FUTURE_* to the tokenizer,
                # which is expected to work independently of them.  It's
                # certainly the case for all futures in Python <= 2.7.
                tokens = pytokenizer.generate_tokens(source_lines, flags)

                self.grammar = pygram.python_grammar

                for tp, value, lineno, column, line in tokens:
                    if self.add_token(tp, value, lineno, column, line):
                        break
            except error.TokenError as e:
                e.filename = compile_info.filename
                raise
            except parser.ParseError as e:
                # Catch parse errors, pretty them up and reraise them as a
                # SyntaxError.
                new_err = error.IndentationError
                if tp == pygram.tokens.INDENT:
                    msg = "unexpected indent"
                elif e.expected == pygram.tokens.INDENT:
                    msg = "expected an indented block"
                else:
                    new_err = error.SyntaxError
                    msg = "invalid syntax"
                raise new_err(msg, e.lineno, e.column, e.line,
                              compile_info.filename)
            else:
                tree = self.root
        finally:
            # Avoid hanging onto the tree.
            self.root = None
        if enc is not None:
            compile_info.encoding = enc
            # Wrap the tree in a special encoding declaration for parser module
            # compatibility.
            tree = parser.NonterminalEnc(pygram.syms.encoding_decl, tree, enc)
        return tree

def parse(filename):
    """returns the parsed contents of <filename>"""
    info = CompileInfo(filename)
    f = open(filename)
    try:
        return PythonParser().parse_source(f.read(), info)
    finally:
        f.close()

def suite(text):
    """returns the parsed form of the given program <text>"""
    info = CompileInfo("<stdin>")
    return PythonParser().parse_source(text, info)

def expr(text):
    """returns the parsed form of the given expression <text>"""
    info = CompileInfo("<stdin>", "single")
    return PythonParser().parse_source(text, info)

def st2tuple(tree, line_info=True, col_info=False):
    """returns <tree> in tuple form for the compiler package"""
    if isinstance(tree, parser.AbstractNonterminal):
        l = [tree.type]
        for i in range(0, tree.num_children()):
            l.append(st2tuple(tree.get_child(i)))
        if isinstance(tree, parser.NonterminalEnc):
            l.append(tree.encoding)
        return tuple(l)
    elif isinstance(tree, parser.Terminal):
        l = [tree.type, tree.value]
        if line_info:
            l.append(tree.get_lineno())
        if col_info:
            l.append(tree.get_column())
        return tuple(l)
    else:
        raise TypeError, tree

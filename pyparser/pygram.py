import os
from pyparser import parser, pytoken, metaparser

class PythonGrammar(parser.Grammar):

    KEYWORD_TOKEN = pytoken.python_tokens["NAME"]
    TOKENS = pytoken.python_tokens
    OPERATOR_MAP = pytoken.python_opmap

def _get_python_grammar():
    here = os.path.dirname(__file__)
    fp = open(os.path.join(here, "data", "Grammar-Lichen"))
    try:
        gram_source = fp.read()
    finally:
        fp.close()
    pgen = metaparser.ParserGenerator(gram_source)
    return pgen.build_grammar(PythonGrammar)


python_grammar = _get_python_grammar()

# For token module compatibility, expose name-to-index and index-to-name
# mappings.

tokens = pytoken.python_tokens
tok_name = pytoken.python_opmap

# For symbol module compatibility, expose name-to-index and index-to-name
# mappings.

syms = python_grammar.symbol_ids
sym_name = {}
for name, idx in python_grammar.symbol_ids.iteritems():
    sym_name[idx] = name

del _get_python_grammar, name, idx

# New parser tests.
import py
import tokenize
import StringIO
from pyparser import parser, metaparser, pygram
from pyparser.test.test_metaparser import MyGrammar
from pyparser.pygram import tokens as token


class SimpleParser(parser.Parser):

    def parse(self, input):
        self.prepare()
        rl = StringIO.StringIO(input + "\n").readline
        gen = tokenize.generate_tokens(rl)
        for tp, value, begin, end, line in gen:
            if self.add_token(tp, value, begin[0], begin[1], line):
                py.test.raises(StopIteration, gen.next)
        return self.root


def tree_from_string(expected, gram):
    def count_indent(s):
        indent = 0
        for char in s:
            if char != " ":
                break
            indent += 1
        return indent
    last_newline_index = 0
    for i, char in enumerate(expected):
        if char == "\n":
            last_newline_index = i
        elif char != " ":
            break
    if last_newline_index:
        expected = expected[last_newline_index + 1:]
    base_indent = count_indent(expected)
    assert not divmod(base_indent, 4)[1], "not using 4 space indentation"
    lines = [line[base_indent:] for line in expected.splitlines()]
    last_indent = 0
    node_stack = []
    for line in lines:
        if not line.strip():
            continue
        data = line.split()
        if data[0].isupper():
            tp = token.get(data[0])
            if len(data) == 2:
                value = data[1].strip("\"")
            elif tp == token["NEWLINE"]:
                value = "\n"
            else:
                value = ""
            n = parser.Terminal(tp, value, 0, 0)
        else:
            tp = gram.symbol_ids[data[0]]
            children = []
            n = parser.Nonterminal(tp, children)
        new_indent = count_indent(line)
        if new_indent >= last_indent:
            if new_indent == last_indent and node_stack:
                node_stack.pop()
            if node_stack:
                node_stack[-1].append_child(n)
            node_stack.append(n)
        else:
            diff = last_indent - new_indent
            pop_nodes = diff // 4 + 1
            del node_stack[-pop_nodes:]
            node_stack[-1].append_child(n)
            node_stack.append(n)
        last_indent = new_indent
    return node_stack[0]


class TestParser:

    def parser_for(self, gram, add_endmarker=True):
        if add_endmarker:
            gram += " NEWLINE ENDMARKER\n"
        pgen = metaparser.ParserGenerator(gram)
        g = pgen.build_grammar(MyGrammar)
        return SimpleParser(g), g

    def test_multiple_rules(self):
        gram = """foo: 'next_rule' bar 'end' NEWLINE ENDMARKER
bar: NAME NUMBER\n"""
        p, gram = self.parser_for(gram, False)
        expected = """
        foo
            NAME "next_rule"
            bar
                NAME "a_name"
                NUMBER "42"
            NAME "end"
            NEWLINE
            ENDMARKER"""
        input = "next_rule a_name 42 end"
        assert tree_from_string(expected, gram) == p.parse(input)

    def test_recursive_rule(self):
        gram = """foo: NAME bar STRING NEWLINE ENDMARKER
bar: NAME [bar] NUMBER\n"""
        p, gram = self.parser_for(gram, False)
        expected = """
        foo
            NAME "hi"
            bar
                NAME "hello"
                bar
                    NAME "a_name"
                    NUMBER "32"
                NUMBER "42"
            STRING "'string'"
            NEWLINE
            ENDMARKER"""
        input = "hi hello a_name 32 42 'string'"
        assert tree_from_string(expected, gram) == p.parse(input)

    def test_symbol(self):
        gram = """parent: first_child second_child NEWLINE ENDMARKER
first_child: NAME age
second_child: STRING
age: NUMBER\n"""
        p, gram = self.parser_for(gram, False)
        expected = """
        parent
            first_child
                NAME "harry"
                age
                     NUMBER "13"
            second_child
                STRING "'fred'"
            NEWLINE
            ENDMARKER"""
        input = "harry 13 'fred'"
        assert tree_from_string(expected, gram) == p.parse(input)

    def test_token(self):
        p, gram = self.parser_for("foo: NAME")
        expected = """
        foo
           NAME "hi"
           NEWLINE
           ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("hi")
        py.test.raises(parser.ParseError, p.parse, "567")
        p, gram = self.parser_for("foo: NUMBER NAME STRING")
        expected = """
        foo
           NUMBER "42"
           NAME "hi"
           STRING "'bar'"
           NEWLINE
           ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("42 hi 'bar'")

    def test_optional(self):
        p, gram = self.parser_for("foo: [NAME] 'end'")
        expected = """
        foo
            NAME "hi"
            NAME "end"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("hi end")
        expected = """
        foo
            NAME "end"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("end")

    def test_grouping(self):
        p, gram = self.parser_for(
            "foo: ((NUMBER NAME | STRING) | 'second_option')")
        expected = """
        foo
            NUMBER "42"
            NAME "hi"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("42 hi")
        expected = """
        foo
            STRING "'hi'"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("'hi'")
        expected = """
        foo
            NAME "second_option"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("second_option")
        py.test.raises(parser.ParseError, p.parse, "42 a_name 'hi'")
        py.test.raises(parser.ParseError, p.parse, "42 second_option")

    def test_alternative(self):
        p, gram = self.parser_for("foo: (NAME | NUMBER)")
        expected = """
        foo
            NAME "hi"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("hi")
        expected = """
        foo
            NUMBER "42"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("42")
        py.test.raises(parser.ParseError, p.parse, "hi 23")
        py.test.raises(parser.ParseError, p.parse, "23 hi")
        py.test.raises(parser.ParseError, p.parse, "'some string'")

    def test_keyword(self):
        p, gram = self.parser_for("foo: 'key'")
        expected = """
        foo
            NAME "key"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("key")
        py.test.raises(parser.ParseError, p.parse, "")
        p, gram = self.parser_for("foo: NAME 'key'")
        expected = """
        foo
            NAME "some_name"
            NAME "key"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("some_name key")
        py.test.raises(parser.ParseError, p.parse, "some_name")

    def test_repeaters(self):
        p, gram = self.parser_for("foo: NAME+ 'end'")
        expected = """
        foo
            NAME "hi"
            NAME "bye"
            NAME "nothing"
            NAME "end"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("hi bye nothing end")
        py.test.raises(parser.ParseError, p.parse, "end")
        py.test.raises(parser.ParseError, p.parse, "hi bye")
        p, gram = self.parser_for("foo: NAME* 'end'")
        expected = """
        foo
            NAME "hi"
            NAME "bye"
            NAME "end"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("hi bye end")
        py.test.raises(parser.ParseError, p.parse, "hi bye")
        expected = """
        foo
            NAME "end"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("end")

        p, gram = self.parser_for("foo: (NAME | NUMBER)+ 'end'")
        expected = """
        foo
            NAME "a_name"
            NAME "name_two"
            NAME "end"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("a_name name_two end")
        expected = """
        foo
            NUMBER "42"
            NAME "name"
            NAME "end"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("42 name end")
        py.test.raises(parser.ParseError, p.parse, "end")
        p, gram = self.parser_for("foo: (NAME | NUMBER)* 'end'")
        expected = """
        foo
            NAME "hi"
            NUMBER 42
            NAME "end"
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse("hi 42 end")

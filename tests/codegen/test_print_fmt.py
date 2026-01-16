"""
Tests for print format string code generation (Phase 5.2).
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator


def generate(source: str) -> str:
    """Helper to parse and generate code from Quasar source."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    # Semantic analysis is removed from this helper for these tests
    # analyzer = SemanticAnalyzer()
    # analyzer.analyze(ast)
    code = CodeGenerator().generate(ast)
    # Strip Phase 13 imports for legacy tests
    code = code.replace("import os as _q_os\nimport sys as _q_sys\n\n", "")
    return code


class TestFormatCodeGeneration:
    """Tests for format string code generation."""
    
    def test_codegen_fmt_simple(self):
        """print('Val: {}', x) -> print('Val: {}'.format(x))"""
        source = 'let x: int = 42\nprint("Val: {}", x)'
        code = generate(source)
        assert 'print("Val: {}".format(x))' in code
    
    def test_codegen_fmt_multi(self):
        """print('{}={}', a, b) -> print('{}={}'.format(a, b))"""
        source = 'let a: int = 1\nlet b: int = 2\nprint("{}={}", a, b)'
        code = generate(source)
        assert 'print("{}={}".format(a, b))' in code
    
    def test_codegen_fmt_three_args(self):
        """print('{}, {}, {}', x, y, z) -> print('{}, {}, {}'.format(x, y, z))"""
        source = 'print("{}, {}, {}", 1, 2, 3)'
        code = generate(source)
        assert 'print("{}, {}, {}".format(1, 2, 3))' in code
    
    def test_codegen_fmt_with_text(self):
        """Format with surrounding text."""
        source = 'let name: str = "Alice"\nprint("Hello, {}!", name)'
        code = generate(source)
        assert 'print("Hello, {}!".format(name))' in code
    
    def test_codegen_fmt_with_end(self):
        """print('Done: {}', x, end='!') -> print('Done: {}'.format(x), end='!')"""
        source = 'let x: int = 99\nprint("Done: {}", x, end="!")'
        code = generate(source)
        assert 'print("Done: {}".format(x), end="!")' in code
    
    def test_codegen_fmt_with_end_newline(self):
        """Format with end parameter as newline."""
        source = 'print("Result: {}", 42, end="\\n\\n")'
        code = generate(source)
        assert 'print("Result: {}".format(42), end="\\n\\n")' in code
    
    def test_codegen_fmt_sep_ignored(self):
        """In format mode, sep is effectively ignored (single output)."""
        source = 'print("{} + {}", 1, 2, sep="-")'
        code = generate(source)
        # Format mode produces single string, sep has no effect
        # Implementation may omit sep or include it (both valid)
        assert '".format(1, 2)' in code
    
    def test_codegen_fmt_escapes(self):
        """print('Set {{}} to {}', x) -> print('Set {{}} to {}'.format(x))"""
        # Python uses same escape sequence for literal braces
        source = 'let x: int = 5\nprint("Set {{}} to {}", x)'
        code = generate(source)
        assert 'print("Set {{}} to {}".format(x))' in code
    
    def test_codegen_fmt_mixed_escapes(self):
        """Mixed escaped and real placeholders."""
        source = 'print("{{name}}: {}", "value")'
        code = generate(source)
        assert 'print("{{name}}: {}".format("value"))' in code


class TestNormalModePreserved:
    """Tests that normal mode is preserved when format rules don't apply."""
    
    def test_codegen_no_fmt_variable_first_arg(self):
        """let f='{}'; print(f, x) -> print(f, x) (no .format)"""
        source = 'let f: str = "{}"\nlet x: int = 1\nprint(f, x)'
        code = generate(source)
        assert "print(f, x)" in code
        assert ".format" not in code
    
    def test_codegen_no_fmt_single_arg_placeholder(self):
        """print('{}') -> print('{}') (no formatting, single arg)"""
        source = 'print("{}")'
        code = generate(source)
        assert 'print("{}")' in code
        assert ".format" not in code
    
    def test_codegen_no_fmt_no_placeholder(self):
        """print('hello', 1, 2) -> print('hello', 1, 2) (no placeholder)"""
        source = 'print("hello", 1, 2)'
        code = generate(source)
        assert 'print("hello", 1, 2)' in code
        assert ".format" not in code
    
    def test_codegen_no_fmt_only_escaped(self):
        """print('{{}}', x) -> print('{{}}', x) (only escaped, no real placeholder)"""
        source = 'let x: int = 1\nprint("{{}}", x)'
        code = generate(source)
        assert 'print("{{}}", x)' in code
        assert ".format" not in code
    
    def test_codegen_normal_with_sep(self):
        """Normal mode with sep preserved."""
        source = 'print("a", "b", "c", sep="-")'
        code = generate(source)
        assert 'print("a", "b", "c", sep="-")' in code
    
    def test_codegen_normal_with_end(self):
        """Normal mode with end preserved."""
        source = 'print("test", end="")'
        code = generate(source)
        assert 'print("test", end="")' in code
    
    def test_codegen_normal_with_sep_and_end(self):
        """Normal mode with both sep and end."""
        source = 'print(1, 2, 3, sep=", ", end="!")'
        code = generate(source)
        assert 'print(1, 2, 3, sep=", ", end="!")' in code


class TestFormatWithExpressions:
    """Tests for format strings with various expression types."""
    
    def test_codegen_fmt_with_int_literal(self):
        """Format with integer literal."""
        source = 'print("Number: {}", 42)'
        code = generate(source)
        assert 'print("Number: {}".format(42))' in code
    
    def test_codegen_fmt_with_float_literal(self):
        """Format with float literal."""
        source = 'print("Pi: {}", 3.14)'
        code = generate(source)
        assert 'print("Pi: {}".format(3.14))' in code
    
    def test_codegen_fmt_with_bool_true(self):
        """Format with boolean true."""
        source = 'print("Active: {}", true)'
        code = generate(source)
        assert 'print("Active: {}".format(True))' in code
    
    def test_codegen_fmt_with_bool_false(self):
        """Format with boolean false."""
        source = 'print("Active: {}", false)'
        code = generate(source)
        assert 'print("Active: {}".format(False))' in code
    
    def test_codegen_fmt_with_string_literal(self):
        """Format with string literal."""
        source = 'print("Name: {}", "Alice")'
        code = generate(source)
        assert 'print("Name: {}".format("Alice"))' in code
    
    def test_codegen_fmt_with_expression(self):
        """Format with arithmetic expression."""
        source = 'print("Sum: {}", 1 + 2)'
        code = generate(source)
        assert 'print("Sum: {}".format((1 + 2)))' in code
    
    def test_codegen_fmt_with_function_call(self):
        """Format with function call."""
        source = """fn double(n: int) -> int {
    return n * 2
}
print("Result: {}", double(5))"""
        code = generate(source)
        assert 'print("Result: {}".format(double(5)))' in code

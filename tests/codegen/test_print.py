"""
Tests for print statement code generation (Phase 5 + 5.1).
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
    code = CodeGenerator().generate(ast)
    # Strip Phase 13 imports for legacy tests
    code = code.replace("import os as _q_os\nimport sys as _q_sys\n\n", "")
    return code


class TestPrintStatementCodeGen:
    """Tests for print statement code generation."""
    
    def test_codegen_print_int(self):
        """print(42) → print(42)"""
        code = generate("print(42)")
        assert code == "print(42)"
    
    def test_codegen_print_float(self):
        """print(3.14) → print(3.14)"""
        code = generate("print(3.14)")
        assert code == "print(3.14)"
    
    def test_codegen_print_true(self):
        """print(true) → print(True)"""
        code = generate("print(true)")
        assert code == "print(True)"
    
    def test_codegen_print_false(self):
        """print(false) → print(False)"""
        code = generate("print(false)")
        assert code == "print(False)"
    
    def test_codegen_print_string(self):
        """print("hello") → print("hello")"""
        code = generate('print("hello")')
        assert code == 'print("hello")'
    
    def test_codegen_print_variable(self):
        """print(x) after let x = 5"""
        code = generate("let x: int = 5\nprint(x)")
        lines = code.split("\n")
        assert lines[0] == "x = 5"
        assert lines[1] == "print(x)"
    
    def test_codegen_print_expression(self):
        """print(2 + 3) → print(2 + 3)"""
        code = generate("print(2 + 3)")
        assert code == "print((2 + 3))"
    
    def test_codegen_print_function_call(self):
        """print(f(5)) → print(f(5))"""
        source = """fn f(n: int) -> int {
    return n
}
print(f(5))"""
        code = generate(source)
        assert "print(f(5))" in code


class TestPrintInContext:
    """Tests for print in various code contexts."""
    
    def test_print_in_function(self):
        """print inside function body"""
        source = """fn greet() -> int {
    print("hello")
    return 0
}"""
        code = generate(source)
        lines = code.split("\n")
        assert any("print(\"hello\")" in line for line in lines)
    
    def test_print_in_loop(self):
        """print inside while loop"""
        source = """let i: int = 0
while i < 3 {
    print(i)
    i = i + 1
}"""
        code = generate(source)
        assert "print(i)" in code
    
    def test_print_in_conditional(self):
        """print inside if/else"""
        source = """let x: int = 5
if x > 0 {
    print("positive")
} else {
    print("non-positive")
}"""
        code = generate(source)
        assert 'print("positive")' in code
        assert 'print("non-positive")' in code
    
    def test_print_multiple_times(self):
        """Multiple print statements"""
        source = """print(1)
print(2)
print(3)"""
        code = generate(source)
        lines = code.split("\n")
        assert lines[0] == "print(1)"
        assert lines[1] == "print(2)"
        assert lines[2] == "print(3)"


class TestPrintMultipleArgsCodeGen:
    """Tests for print with multiple arguments (Phase 5.1)."""
    
    def test_codegen_print_two_args(self):
        """print(1, 2) → print(1, 2)"""
        code = generate("print(1, 2)")
        assert code == "print(1, 2)"
    
    def test_codegen_print_three_args(self):
        """print(1, 2, 3) → print(1, 2, 3)"""
        code = generate("print(1, 2, 3)")
        assert code == "print(1, 2, 3)"
    
    def test_codegen_print_mixed_types(self):
        """print with mixed types"""
        code = generate('print("x =", 42, true)')
        assert code == 'print("x =", 42, True)'
    
    def test_codegen_print_variables(self):
        """print with multiple variables"""
        code = generate("let a: int = 1\nlet b: int = 2\nprint(a, b)")
        lines = code.split("\n")
        assert lines[2] == "print(a, b)"
    
    def test_codegen_print_expressions(self):
        """print with expressions"""
        code = generate("print(1 + 2, 3 * 4)")
        assert code == "print((1 + 2), (3 * 4))"


class TestPrintSepEndCodeGen:
    """Tests for print with sep/end parameters (Phase 5.1)."""
    
    def test_codegen_print_with_sep(self):
        """print(1, 2, sep=',') → print(1, 2, sep=',')"""
        code = generate('print(1, 2, sep=",")')
        assert code == 'print(1, 2, sep=",")'
    
    def test_codegen_print_with_end(self):
        """print(1, end='') → print(1, end='')"""
        code = generate('print(1, end="")')
        assert code == 'print(1, end="")'
    
    def test_codegen_print_with_sep_and_end(self):
        """print(1, 2, sep='-', end='!') → print(1, 2, sep='-', end='!')"""
        code = generate('print(1, 2, sep="-", end="!")')
        assert code == 'print(1, 2, sep="-", end="!")'
    
    def test_codegen_print_sep_variable(self):
        """print with sep as variable"""
        code = generate('let s: str = ","\nprint(1, 2, sep=s)')
        lines = code.split("\n")
        assert lines[1] == "print(1, 2, sep=s)"
    
    def test_codegen_print_end_variable(self):
        """print with end as variable"""
        code = generate('let e: str = ""\nprint(1, end=e)')
        lines = code.split("\n")
        assert lines[1] == "print(1, end=e)"
    
    def test_codegen_print_many_args_sep_end(self):
        """print with many args and sep/end"""
        code = generate('print(1, 2, 3, 4, 5, sep=", ", end="\\n")')
        assert code == 'print(1, 2, 3, 4, 5, sep=", ", end="\\n")'
    
    def test_codegen_print_single_arg_end(self):
        """print single arg with end (no sep needed)"""
        code = generate('print(42, end="")')
        assert code == 'print(42, end="")'
    
    def test_codegen_print_labeled_output(self):
        """print('Label:', value) pattern"""
        code = generate('let x: int = 100\nprint("Result:", x)')
        lines = code.split("\n")
        assert lines[1] == 'print("Result:", x)'
    
    def test_codegen_print_csv_style(self):
        """print CSV-style output"""
        code = generate('print("a", "b", "c", sep=",")')
        assert code == 'print("a", "b", "c", sep=",")'
    
    def test_codegen_print_inline_no_newline(self):
        """print without newline for inline output"""
        code = generate('print("Loading", end="")')
        assert code == 'print("Loading", end="")'

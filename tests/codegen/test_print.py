"""
Tests for print statement code generation (Phase 5).
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator


def generate(source: str) -> str:
    """Helper to generate Python code from Quasar source."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    generator = CodeGenerator()
    return generator.generate(ast)


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
        assert code == "print(2 + 3)"
    
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

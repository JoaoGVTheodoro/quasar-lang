"""
Tests for code generation of complete programs.

End-to-end tests with multiple declarations and complex structures.

Note: Quasar grammar does NOT use semicolons as statement terminators.
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.codegen import CodeGenerator


def generate(source: str) -> str:
    """Helper to parse and generate code from Quasar source."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    return CodeGenerator().generate(ast)


class TestMultipleDeclarations:
    """Tests for programs with multiple declarations."""
    
    def test_multiple_vars(self):
        source = """
        let a: int = 1
        let b: int = 2
        let c: int = 3
        """
        result = generate(source)
        expected = "a = 1\nb = 2\nc = 3"
        assert result == expected
    
    def test_vars_and_consts(self):
        source = """
        const PI: float = 3.14
        let radius: float = 2.0
        """
        result = generate(source)
        expected = "PI = 3.14\nradius = 2.0"
        assert result == expected
    
    def test_multiple_functions(self):
        source = """
        fn first() -> int { return 1 }
        fn second() -> int { return 2 }
        """
        result = generate(source)
        expected = "def first():\n    return 1\n\ndef second():\n    return 2"
        assert result == expected


class TestComplexPrograms:
    """Tests for complex programs with various constructs."""
    
    def test_function_with_conditionals(self):
        source = """
        fn abs(x: int) -> int {
            if x < 0 {
                return -x
            }
            return x
        }
        """
        result = generate(source)
        expected = "def abs(x):\n    if (x < 0):\n        return -x\n    return x"
        assert result == expected
    
    def test_function_with_loop(self):
        source = """
        fn countdown(n: int) -> int {
            let i: int = n
            while i > 0 {
                i = i - 1
            }
            return i
        }
        """
        result = generate(source)
        expected = "def countdown(n):\n    i = n\n    while (i > 0):\n        i = (i - 1)\n    return i"
        assert result == expected
    
    def test_function_calling_function(self):
        source = """
        fn helper(x: int) -> int { return x + 1 }
        fn main() -> int { return helper(41) }
        """
        result = generate(source)
        assert "def helper(x):" in result
        assert "return (x + 1)" in result
        assert "def main():" in result
        assert "return helper(41)" in result
    
    def test_global_and_function(self):
        source = """
        const LIMIT: int = 100
        fn check(x: int) -> bool {
            return x < LIMIT
        }
        """
        result = generate(source)
        assert "LIMIT = 100" in result
        assert "def check(x):" in result
        assert "return (x < LIMIT)" in result


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_empty_program(self):
        source = ""
        result = generate(source)
        assert result == ""
    
    def test_deeply_nested(self):
        source = """
        fn deep(a: bool, b: bool, c: bool) -> int {
            if a {
                if b {
                    if c {
                        return 1
                    }
                }
            }
            return 0
        }
        """
        result = generate(source)
        # Should have proper 4-space indentation at each level
        assert "        if c:" in result
        assert "            return 1" in result
    
    def test_complex_expression(self):
        source = "let x: bool = 1 + 2 * 3 > 5 && true"
        result = generate(source)
        assert result == "x = (((1 + (2 * 3)) > 5) and True)"
    
    def test_string_with_escape(self):
        source = r'let x: str = "hello\nworld"'
        result = generate(source)
        assert 'x = "hello\\nworld"' in result

"""
Tests for code generation of expressions.

Covers: BinaryExpr, UnaryExpr, CallExpr, Identifier

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


class TestArithmeticOperators:
    """Tests for arithmetic operator generation."""
    
    def test_addition(self):
        source = "let x: int = 1 + 2"
        result = generate(source)
        assert result == "x = 1 + 2"
    
    def test_subtraction(self):
        source = "let x: int = 5 - 3"
        result = generate(source)
        assert result == "x = 5 - 3"
    
    def test_multiplication(self):
        source = "let x: int = 4 * 2"
        result = generate(source)
        assert result == "x = 4 * 2"
    
    def test_division(self):
        source = "let x: int = 10 / 2"
        result = generate(source)
        assert result == "x = 10 / 2"
    
    def test_modulo(self):
        source = "let x: int = 10 % 3"
        result = generate(source)
        assert result == "x = 10 % 3"
    
    def test_string_concatenation(self):
        source = 'let x: str = "hello" + "world"'
        result = generate(source)
        assert result == 'x = "hello" + "world"'


class TestComparisonOperators:
    """Tests for comparison operator generation."""
    
    def test_equal(self):
        source = "let x: bool = 1 == 1"
        result = generate(source)
        assert result == "x = 1 == 1"
    
    def test_not_equal(self):
        source = "let x: bool = 1 != 2"
        result = generate(source)
        assert result == "x = 1 != 2"
    
    def test_less_than(self):
        source = "let x: bool = 1 < 2"
        result = generate(source)
        assert result == "x = 1 < 2"
    
    def test_greater_than(self):
        source = "let x: bool = 2 > 1"
        result = generate(source)
        assert result == "x = 2 > 1"
    
    def test_less_equal(self):
        source = "let x: bool = 1 <= 2"
        result = generate(source)
        assert result == "x = 1 <= 2"
    
    def test_greater_equal(self):
        source = "let x: bool = 2 >= 1"
        result = generate(source)
        assert result == "x = 2 >= 1"


class TestLogicalOperators:
    """Tests for logical operator generation."""
    
    def test_and(self):
        source = "let x: bool = true && false"
        result = generate(source)
        assert result == "x = True and False"
    
    def test_or(self):
        source = "let x: bool = true || false"
        result = generate(source)
        assert result == "x = True or False"
    
    def test_not(self):
        source = "let x: bool = !true"
        result = generate(source)
        assert result == "x = not True"


class TestUnaryOperators:
    """Tests for unary operator generation."""
    
    def test_negation(self):
        source = "let x: int = -42"
        result = generate(source)
        assert result == "x = -42"
    
    def test_negation_float(self):
        source = "let x: float = -3.14"
        result = generate(source)
        assert result == "x = -3.14"


class TestCallExpr:
    """Tests for function call generation."""
    
    def test_call_no_args(self):
        source = """
        fn getValue() -> int { return 1 }
        fn main() -> int { return getValue() }
        """
        result = generate(source)
        assert "return getValue()" in result
    
    def test_call_one_arg(self):
        source = """
        fn double(x: int) -> int { return x }
        fn main() -> int { return double(5) }
        """
        result = generate(source)
        assert "return double(5)" in result
    
    def test_call_multiple_args(self):
        source = """
        fn add(a: int, b: int) -> int { return a }
        fn main() -> int { return add(1, 2) }
        """
        result = generate(source)
        assert "return add(1, 2)" in result


class TestIdentifier:
    """Tests for identifier generation."""
    
    def test_identifier_in_expression(self):
        source = """
        fn use(x: int) -> int {
            return x
        }
        """
        result = generate(source)
        assert "return x" in result
    
    def test_identifier_in_binary(self):
        source = """
        fn calc(a: int, b: int) -> int {
            return a + b
        }
        """
        result = generate(source)
        assert "return a + b" in result


class TestPrecedence:
    """Tests for operator precedence in generation."""
    
    def test_precedence_mul_add(self):
        source = "let x: int = 1 + 2 * 3"
        result = generate(source)
        # Parser should have handled precedence, codegen preserves structure
        assert result == "x = 1 + 2 * 3"
    
    def test_precedence_comparison_logical(self):
        source = "let x: bool = 1 < 2 && 3 > 1"
        result = generate(source)
        assert result == "x = 1 < 2 and 3 > 1"

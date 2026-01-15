"""
Semantic Analysis tests — Type errors.

Tests that type violations produce appropriate semantic errors.
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer, SemanticError


def analyze(source: str):
    """Helper to run semantic analysis on source."""
    lexer = Lexer(source, "test.qsr")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)


def expect_error(source: str, error_code: str):
    """Helper to verify semantic error with specific code."""
    with pytest.raises(SemanticError) as exc_info:
        analyze(source)
    assert exc_info.value.code == error_code
    return exc_info.value


class TestTypeMismatch:
    """Test E0100: Type mismatch in declaration."""
    
    def test_int_declared_as_float(self) -> None:
        """Declaring int with float value should produce E0100."""
        source = "let x: int = 3.14"
        expect_error(source, "E0100")
    
    def test_float_declared_as_int(self) -> None:
        """Declaring float with int value should produce E0100."""
        source = "let x: float = 42"
        expect_error(source, "E0100")
    
    def test_bool_declared_as_int(self) -> None:
        """Declaring bool with int value should produce E0100."""
        source = "let x: bool = 1"
        expect_error(source, "E0100")
    
    def test_str_declared_as_int(self) -> None:
        """Declaring str with int value should produce E0100."""
        source = "let x: str = 42"
        expect_error(source, "E0100")


class TestConditionType:
    """Test E0101: Non-boolean condition."""
    
    def test_if_int_condition(self) -> None:
        """if with int condition should produce E0101."""
        source = """
fn f() -> int {
    let x: int = 1
    if (x) { }
}
"""
        expect_error(source, "E0101")
    
    def test_if_str_condition(self) -> None:
        """if with str condition should produce E0101."""
        source = """
fn f() -> int {
    let x: str = "hello"
    if (x) { }
}
"""
        expect_error(source, "E0101")
    
    def test_while_int_condition(self) -> None:
        """while with int condition should produce E0101."""
        source = """
fn f() -> int {
    let x: int = 1
    while (x) { break }
}
"""
        expect_error(source, "E0101")
    
    def test_while_float_condition(self) -> None:
        """while with float condition should produce E0101."""
        source = """
fn f() -> int {
    while (1.0) { break }
}
"""
        expect_error(source, "E0101")


class TestBinaryOperatorTypes:
    """Test E0102/E0103: Invalid operand types for operators."""
    
    def test_add_int_float(self) -> None:
        """Adding int and float should produce type error (D-CF-5)."""
        source = """
fn f() -> int {
    let a: int = 1
    let b: float = 2.0
    let c: int = a + b
}
"""
        expect_error(source, "E0102")
    
    def test_multiply_int_float(self) -> None:
        """Multiplying int and float should produce type error."""
        source = """
fn f() -> int {
    let a: int = 1
    let b: float = 2.0
    let c: int = a * b
}
"""
        expect_error(source, "E0102")
    
    def test_add_string_int(self) -> None:
        """Adding string and int should produce type error."""
        source = """
fn f() -> int {
    let a: str = "hello"
    let b: int = 1
    let c: str = a + b
}
"""
        expect_error(source, "E0102")
    
    def test_string_comparison_lt(self) -> None:
        """String comparison with < should produce type error (D-CF-8)."""
        source = """
fn f() -> int {
    let a: str = "a"
    let b: str = "b"
    let c: bool = a < b
}
"""
        expect_error(source, "E0103")
    
    def test_string_comparison_gt(self) -> None:
        """String comparison with > should produce type error."""
        source = """
fn f() -> int {
    let a: str = "a"
    let b: str = "b"
    let c: bool = a > b
}
"""
        expect_error(source, "E0103")


class TestLogicalOperatorTypes:
    """Test E0104: Invalid operand types for logical operators."""
    
    def test_and_with_int(self) -> None:
        """&& with int operand should produce E0104."""
        source = """
fn f() -> int {
    let a: int = 1
    let b: bool = true
    let c: bool = a && b
}
"""
        expect_error(source, "E0104")
    
    def test_or_with_string(self) -> None:
        """|| with string operand should produce E0104."""
        source = """
fn f() -> int {
    let a: str = "hello"
    let b: bool = true
    let c: bool = a || b
}
"""
        expect_error(source, "E0104")
    
    def test_not_with_int(self) -> None:
        """! with int operand should produce E0104."""
        source = """
fn f() -> int {
    let x: int = 1
    let y: bool = !x
}
"""
        expect_error(source, "E0104")


class TestValidTypes:
    """Test valid type usage (should NOT produce errors)."""
    
    def test_string_concatenation(self) -> None:
        """String + string should be allowed (D-CF-7)."""
        source = """
fn f() -> int {
    let a: str = "hello"
    let b: str = " world"
    let c: str = a + b
}
"""
        # Should NOT raise error
        analyze(source)
    
    def test_string_equality(self) -> None:
        """String == string should be allowed."""
        source = """
fn f() -> int {
    let a: str = "hello"
    let b: str = "world"
    let c: bool = a == b
}
"""
        # Should NOT raise error
        analyze(source)
    
    def test_int_arithmetic(self) -> None:
        """int + int should be allowed."""
        source = """
fn f() -> int {
    let a: int = 1
    let b: int = 2
    let c: int = a + b
}
"""
        # Should NOT raise error
        analyze(source)
    
    def test_float_arithmetic(self) -> None:
        """float + float should be allowed."""
        source = """
fn f() -> int {
    let a: float = 1.0
    let b: float = 2.0
    let c: float = a + b
}
"""
        # Should NOT raise error
        analyze(source)
    
    def test_boolean_comparison(self) -> None:
        """bool condition should be allowed."""
        source = """
fn f() -> int {
    let a: int = 1
    let b: int = 2
    if (a < b) { }
}
"""
        # Should NOT raise error
        analyze(source)

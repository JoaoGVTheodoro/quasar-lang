"""
Hardening Tests: Division by Zero Detection

Tests for E0104 (literal division by zero).
"""
import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.semantic.errors import SemanticError


def analyze(source: str):
    lexer = Lexer(source)
    program = Parser(lexer.tokenize()).parse()
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)


class TestE0104DivisionByZero:
    """E0104: Division by zero with literal zero."""

    def test_int_division_by_zero(self):
        """10 / 0 should be E0104."""
        source = """
fn f() -> void {
    let x: int = 10 / 0
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0104"
        assert "division by zero" in excinfo.value.message

    def test_int_modulo_by_zero(self):
        """10 % 0 should be E0104."""
        source = """
fn f() -> void {
    let x: int = 10 % 0
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0104"

    def test_float_division_by_zero(self):
        """10.0 / 0.0 should be E0104."""
        source = """
fn f() -> void {
    let x: float = 10.0 / 0.0
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0104"

    def test_expression_division_by_zero(self):
        """(5 + 5) / 0 should be E0104."""
        source = """
fn f() -> void {
    let x: int = (5 + 5) / 0
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0104"


class TestValidDivision:
    """Valid division patterns that should NOT produce errors."""

    def test_division_by_variable(self):
        """10 / y should pass (runtime check only)."""
        source = """
fn f(y: int) -> void {
    let x: int = 10 / y
}
"""
        analyze(source)

    def test_division_by_nonzero_literal(self):
        """10 / 2 should pass."""
        source = """
fn f() -> void {
    let x: int = 10 / 2
}
"""
        analyze(source)

    def test_modulo_by_nonzero_literal(self):
        """10 % 3 should pass."""
        source = """
fn f() -> void {
    let x: int = 10 % 3
}
"""
        analyze(source)


class TestDuplicateParameters:
    """Test that duplicate parameters are caught (E0002)."""

    def test_duplicate_param_names(self):
        """fn f(x: int, x: int) should be E0002."""
        source = """
fn f(x: int, x: int) -> int {
    return x
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0002"
        assert "redeclaration" in excinfo.value.message

    def test_shadow_param_in_nested_block(self):
        """Shadowing param in nested block should pass."""
        source = """
fn f(x: int) -> void {
    if true {
        let x: int = 10
    }
}
"""
        analyze(source)

"""
Hardening Tests: Return Path Analysis

Tests for E0303 (missing return) and E0304 (return outside function).
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


class TestE0304ReturnOutsideFunction:
    """E0304: Return statement outside of function."""

    def test_return_at_module_level(self):
        """Return at module level should be E0304."""
        with pytest.raises(SemanticError) as excinfo:
            analyze("return 42")
        assert excinfo.value.code == "E0304"
        assert "outside of function" in excinfo.value.message

    def test_return_after_function(self):
        """Return after function definition should be E0304."""
        source = """
fn f() -> int {
    return 1
}
return 42
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0304"


class TestE0303MissingReturn:
    """E0303: Missing return in non-void function."""

    def test_missing_return_empty_body(self):
        """Non-void function with no return should be E0303."""
        source = """
fn get_value() -> int {
    let x: int = 42
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0303"
        assert "may not return" in excinfo.value.message

    def test_missing_return_if_only(self):
        """Non-void function with return only in if (no else) should be E0303."""
        source = """
fn get_value(x: int) -> int {
    if x > 0 {
        return x
    }
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0303"

    def test_missing_return_if_else_partial(self):
        """Return in only one branch should be E0303."""
        source = """
fn get_value(x: int) -> int {
    if x > 0 {
        return x
    } else {
        let y: int = 0
    }
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0303"

    def test_missing_return_while_only(self):
        """Return inside while only should be E0303 (loop may not execute)."""
        source = """
fn get_value(x: int) -> int {
    while x > 0 {
        return x
    }
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0303"


class TestValidReturns:
    """Valid return patterns that should NOT produce errors."""

    def test_simple_return(self):
        """Direct return should pass."""
        source = """
fn get_value() -> int {
    return 42
}
"""
        analyze(source)

    def test_if_else_both_return(self):
        """Return in both if and else branches should pass."""
        source = """
fn get_value(x: int) -> int {
    if x > 0 {
        return x
    } else {
        return 0
    }
}
"""
        analyze(source)

    def test_nested_if_else_all_return(self):
        """Nested if/else all returning should pass."""
        source = """
fn classify(x: int) -> int {
    if x > 0 {
        if x > 10 {
            return 2
        } else {
            return 1
        }
    } else {
        return 0
    }
}
"""
        analyze(source)

    def test_void_function_no_return(self):
        """Void function without return should pass."""
        source = """
fn do_nothing() -> void {
    let x: int = 42
}
"""
        analyze(source)

    def test_void_function_with_work(self):
        """Void function doing work without return should pass."""
        source = """
fn process(x: int) -> void {
    let y: int = x + 1
    if y > 0 {
        let z: int = y * 2
    }
}
"""
        analyze(source)

    def test_return_after_if(self):
        """Return after if statement should pass."""
        source = """
fn get_value(x: int) -> int {
    if x > 0 {
        let y: int = x
    }
    return 0
}
"""
        analyze(source)

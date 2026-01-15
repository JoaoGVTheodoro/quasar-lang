"""
Semantic Analysis tests — Control flow errors.

Tests that control flow violations produce appropriate semantic errors.
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


class TestBreakOutsideLoop:
    """Test E0200: break outside of loop."""
    
    def test_break_in_function(self) -> None:
        """break outside of loop should produce E0200."""
        source = """
fn f() -> int {
    break
}
"""
        expect_error(source, "E0200")
    
    def test_break_in_if(self) -> None:
        """break inside if but not in loop should produce E0200."""
        source = """
fn f() -> int {
    if (true) {
        break
    }
}
"""
        expect_error(source, "E0200")
    
    def test_break_after_loop(self) -> None:
        """break after loop ends should produce E0200."""
        source = """
fn f() -> int {
    while (true) { }
    break
}
"""
        expect_error(source, "E0200")


class TestContinueOutsideLoop:
    """Test E0201: continue outside of loop."""
    
    def test_continue_in_function(self) -> None:
        """continue outside of loop should produce E0201."""
        source = """
fn f() -> int {
    continue
}
"""
        expect_error(source, "E0201")
    
    def test_continue_in_if(self) -> None:
        """continue inside if but not in loop should produce E0201."""
        source = """
fn f() -> int {
    if (true) {
        continue
    }
}
"""
        expect_error(source, "E0201")


class TestValidBreakContinue:
    """Test valid break/continue usage."""
    
    def test_break_in_while(self) -> None:
        """break inside while should be allowed."""
        source = """
fn f() -> int {
    while (true) {
        break
    }
}
"""
        # Should NOT raise error
        analyze(source)
    
    def test_continue_in_while(self) -> None:
        """continue inside while should be allowed."""
        source = """
fn f() -> int {
    while (true) {
        continue
    }
}
"""
        # Should NOT raise error
        analyze(source)
    
    def test_break_in_nested_if(self) -> None:
        """break inside if inside while should be allowed."""
        source = """
fn f() -> int {
    while (true) {
        if (true) {
            break
        }
    }
}
"""
        # Should NOT raise error
        analyze(source)
    
    def test_break_in_nested_while(self) -> None:
        """break in nested while should only exit inner loop."""
        source = """
fn f() -> int {
    while (true) {
        while (false) {
            break
        }
    }
}
"""
        # Should NOT raise error
        analyze(source)


class TestReturnErrors:
    """Test E0302: Return type mismatch errors."""
    
    def test_return_wrong_type(self) -> None:
        """return with wrong type should produce E0302."""
        source = """
fn f() -> int {
    return 3.14
}
"""
        expect_error(source, "E0302")
    
    def test_return_string_for_int(self) -> None:
        """return string for int function should produce E0302."""
        source = """
fn f() -> int {
    return "hello"
}
"""
        expect_error(source, "E0302")


class TestValidReturns:
    """Test valid return usage."""
    
    def test_return_matching_type(self) -> None:
        """return with matching type should be allowed."""
        source = """
fn f() -> int {
    return 42
}
"""
        # Should NOT raise error
        analyze(source)
    
    def test_return_expression(self) -> None:
        """return with expression of correct type should be allowed."""
        source = """
fn f() -> int {
    let x: int = 1
    let y: int = 2
    return x + y
}
"""
        # Should NOT raise error
        analyze(source)

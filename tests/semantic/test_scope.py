"""
Semantic Analysis tests — Scope errors.

Tests that scope violations produce appropriate semantic errors.
These tests require the semantic analyzer to be implemented.
"""

import pytest

# NOTE: This module defines the test structure for semantic analysis.
# The actual tests will fail until the semantic analyzer is implemented.
# This is intentional - the tests define the expected behavior.

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


class TestUndeclaredVariable:
    """Test E0001: Use of undeclared identifier."""
    
    def test_undeclared_in_expression(self) -> None:
        """Using undeclared variable should produce E0001."""
        source = "fn f() -> int { let x: int = y }"
        expect_error(source, "E0001")
    
    def test_undeclared_in_assignment(self) -> None:
        """Assigning to undeclared variable should produce E0001."""
        source = "fn f() -> int { x = 1 }"
        expect_error(source, "E0001")
    
    def test_undeclared_in_return(self) -> None:
        """Returning undeclared variable should produce E0001."""
        source = "fn f() -> int { return x }"
        expect_error(source, "E0001")
    
    def test_undeclared_in_condition(self) -> None:
        """Using undeclared variable in condition should produce E0001."""
        source = "fn f() -> int { if (x) { } }"
        expect_error(source, "E0001")


class TestRedeclaration:
    """Test E0002: Redeclaration in same scope."""
    
    def test_redeclare_let_in_same_scope(self) -> None:
        """Redeclaring let in same scope should produce E0002."""
        source = """
fn f() -> int {
    let x: int = 1
    let x: int = 2
}
"""
        expect_error(source, "E0002")
    
    def test_redeclare_const_in_same_scope(self) -> None:
        """Redeclaring const in same scope should produce E0002."""
        source = """
const X: int = 1
const X: int = 2
"""
        expect_error(source, "E0002")
    
    def test_redeclare_param_as_local(self) -> None:
        """Redeclaring parameter as local should produce E0002."""
        source = """
fn f(x: int) -> int {
    let x: int = 1
    return x
}
"""
        expect_error(source, "E0002")
    
    def test_redeclare_function(self) -> None:
        """Redeclaring function should produce E0002."""
        source = """
fn f() -> int { }
fn f() -> int { }
"""
        expect_error(source, "E0002")


class TestShadowing:
    """Test legal shadowing in nested scopes."""
    
    def test_shadow_in_nested_block(self) -> None:
        """Shadowing in nested block should be allowed."""
        source = """
fn f() -> int {
    let x: int = 1
    if (true) {
        let x: int = 2
    }
}
"""
        # Should NOT raise error
        analyze(source)
    
    def test_shadow_global_in_function(self) -> None:
        """Shadowing global in function should be allowed."""
        source = """
let x: int = 1
fn f() -> int {
    let x: int = 2
}
"""
        # Should NOT raise error
        analyze(source)
    
    def test_shadow_in_while_body(self) -> None:
        """Shadowing in while body should be allowed."""
        source = """
fn f() -> int {
    let x: int = 1
    while (true) {
        let x: int = 2
        break
    }
}
"""
        # Should NOT raise error
        analyze(source)


class TestConstAssignment:
    """Test E0003: Assignment to constant."""
    
    def test_assign_to_const(self) -> None:
        """Assigning to const should produce E0003."""
        source = """
const X: int = 1
fn f() -> int {
    X = 2
}
"""
        expect_error(source, "E0003")
    
    def test_assign_to_local_const(self) -> None:
        """Assigning to local const should produce E0003."""
        source = """
fn f() -> int {
    const x: int = 1
    x = 2
}
"""
        expect_error(source, "E0003")

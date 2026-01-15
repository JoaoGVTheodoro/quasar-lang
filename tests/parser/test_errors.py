"""
Parser tests — Error handling.

Tests that invalid syntax produces appropriate parser errors.
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser, ParserError


def parse(source: str):
    """Helper to parse source."""
    lexer = Lexer(source, "test.qsr")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


class TestDeclarationErrors:
    """Test declaration syntax errors."""
    
    def test_let_missing_colon(self) -> None:
        """let x int = 1 should fail (missing colon)."""
        with pytest.raises(ParserError) as exc_info:
            parse("let x int = 1")
        assert ":" in exc_info.value.message
    
    def test_let_missing_type(self) -> None:
        """let x: = 1 should fail (missing type)."""
        with pytest.raises(ParserError):
            parse("let x: = 1")
    
    def test_let_missing_equal(self) -> None:
        """let x: int 1 should fail (missing =)."""
        with pytest.raises(ParserError) as exc_info:
            parse("let x: int 1")
        assert "=" in exc_info.value.message
    
    def test_let_missing_initializer(self) -> None:
        """let x: int = should fail (missing initializer)."""
        with pytest.raises(ParserError):
            parse("let x: int =")
    
    def test_fn_missing_lparen(self) -> None:
        """fn foo -> int { } should fail (missing parentheses)."""
        with pytest.raises(ParserError) as exc_info:
            parse("fn foo -> int { }")
        assert "(" in exc_info.value.message
    
    def test_fn_missing_rparen(self) -> None:
        """fn foo( -> int { } should fail (missing closing paren)."""
        with pytest.raises(ParserError) as exc_info:
            parse("fn foo( -> int { }")
        # Error could be about expecting parameter name or closing paren
        assert ")" in exc_info.value.message or "parameter" in exc_info.value.message
    
    def test_fn_missing_lbrace(self) -> None:
        """fn foo() -> int } should fail (missing opening brace)."""
        with pytest.raises(ParserError) as exc_info:
            parse("fn foo() -> int }")
        assert "{" in exc_info.value.message
    
    def test_fn_param_missing_colon(self) -> None:
        """fn foo(x int) -> int { } should fail (missing colon in param)."""
        with pytest.raises(ParserError):
            parse("fn foo(x int) -> int { return 0 }")


class TestStatementErrors:
    """Test statement syntax errors."""
    
    def test_if_missing_lparen(self) -> None:
        """if true) { } should fail."""
        with pytest.raises(ParserError):
            parse("fn f() -> int { if true) { } return 0 }")
    
    def test_if_missing_rparen(self) -> None:
        """if (true { } should fail."""
        with pytest.raises(ParserError):
            parse("fn f() -> int { if (true { } return 0 }")
    
    def test_if_missing_lbrace(self) -> None:
        """if (true) } should fail."""
        with pytest.raises(ParserError):
            parse("fn f() -> int { if (true) } return 0 }")
    
    def test_while_missing_lparen(self) -> None:
        """while true) { } should fail."""
        with pytest.raises(ParserError):
            parse("fn f() -> int { while true) { } return 0 }")
    
    def test_while_missing_body(self) -> None:
        """while (true) should fail (missing body)."""
        with pytest.raises(ParserError):
            parse("fn f() -> int { while (true) return 0 }")


class TestExpressionErrors:
    """Test expression syntax errors."""
    
    def test_missing_operand(self) -> None:
        """1 + should fail (missing right operand)."""
        with pytest.raises(ParserError):
            parse("fn f() -> int { return 1 + }")
    
    def test_missing_closing_paren(self) -> None:
        """(1 + 2 should fail (missing closing paren)."""
        with pytest.raises(ParserError):
            parse("fn f() -> int { return (1 + 2 }")
    
    def test_call_missing_closing_paren(self) -> None:
        """foo(1, 2 should fail."""
        with pytest.raises(ParserError):
            parse("fn f() -> int { foo(1, 2 }")
    
    def test_empty_parens_not_expression(self) -> None:
        """return () should fail (empty parens)."""
        with pytest.raises(ParserError):
            parse("fn f() -> int { return () }")


class TestErrorLocation:
    """Test that parser errors have correct location."""
    
    def test_error_has_span(self) -> None:
        """Parser error should include span information."""
        with pytest.raises(ParserError) as exc_info:
            parse("let x int = 1")
        assert exc_info.value.span is not None
    
    def test_error_on_correct_line(self) -> None:
        """Parser error should indicate correct line."""
        source = "let x: int = 1\nlet y int = 2"
        with pytest.raises(ParserError) as exc_info:
            parse(source)
        # Error is on line 2 (missing colon)
        assert exc_info.value.span.start_line == 2

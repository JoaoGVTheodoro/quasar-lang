"""
Lexer tests — Span tracking.

Tests that tokens have correct source location spans.
"""

import pytest

from quasar.lexer import Lexer


class TestSingleTokenSpan:
    """Test span for single tokens."""
    
    def test_first_token_starts_at_1_1(self) -> None:
        """First token should start at line 1, column 1."""
        lexer = Lexer("let", "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].span.start_line == 1
        assert tokens[0].span.start_column == 1
    
    def test_token_span_length(self) -> None:
        """Token span should cover the entire lexeme."""
        lexer = Lexer("let", "test.qsr")
        tokens = lexer.tokenize()
        # "let" is 3 characters: columns 1, 2, 3
        assert tokens[0].span.start_column == 1
        assert tokens[0].span.end_column == 3
    
    def test_token_span_same_line(self) -> None:
        """Single-line token should have same start and end line."""
        lexer = Lexer("identifier", "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].span.start_line == tokens[0].span.end_line


class TestMultipleTokenSpans:
    """Test spans for multiple tokens."""
    
    def test_second_token_position(self) -> None:
        """Second token should start after first token plus whitespace."""
        lexer = Lexer("let x", "test.qsr")
        tokens = lexer.tokenize()
        # "let" ends at column 3, space at 4, "x" at 5
        assert tokens[1].span.start_column == 5
    
    def test_tokens_on_multiple_lines(self) -> None:
        """Tokens on different lines should have correct line numbers."""
        lexer = Lexer("let\nx", "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[0].span.start_line == 1
        assert tokens[1].span.start_line == 2
    
    def test_token_after_newline_starts_at_column_1(self) -> None:
        """Token after newline should start at column 1."""
        lexer = Lexer("let\nx", "test.qsr")
        tokens = lexer.tokenize()
        assert tokens[1].span.start_column == 1


class TestStringLiteralSpan:
    """Test span for string literals."""
    
    def test_string_span_includes_quotes(self) -> None:
        """String literal span should include the quotes."""
        lexer = Lexer('"hello"', "test.qsr")
        tokens = lexer.tokenize()
        # "hello" is 7 characters including quotes
        assert tokens[0].span.start_column == 1
        assert tokens[0].span.end_column == 7


class TestMultiCharOperatorSpan:
    """Test span for multi-character operators."""
    
    @pytest.mark.parametrize("source,length", [
        ("==", 2),
        ("!=", 2),
        ("<=", 2),
        (">=", 2),
        ("&&", 2),
        ("||", 2),
        ("->", 2),
    ])
    def test_two_char_operator_span(self, source: str, length: int) -> None:
        """Two-character operators should span 2 columns."""
        lexer = Lexer(source, "test.qsr")
        tokens = lexer.tokenize()
        span = tokens[0].span
        assert span.end_column - span.start_column + 1 == length


class TestEOFSpan:
    """Test span for EOF token."""
    
    def test_eof_span_at_end(self) -> None:
        """EOF token should be at end of source."""
        lexer = Lexer("x", "test.qsr")
        tokens = lexer.tokenize()
        eof = tokens[-1]
        # After "x" at column 1, EOF is at column 2
        assert eof.span.start_column == 2
    
    def test_eof_span_on_last_line(self) -> None:
        """EOF token should be on last line of source."""
        lexer = Lexer("x\ny", "test.qsr")
        tokens = lexer.tokenize()
        eof = tokens[-1]
        assert eof.span.start_line == 2

"""
Lexer tests — Error handling.

Tests that invalid input produces appropriate lexer errors.
"""

import pytest

from quasar.lexer import Lexer, LexerError


class TestUnterminatedString:
    """Test unterminated string detection."""
    
    def test_unterminated_string_eof(self) -> None:
        """Unterminated string at EOF should raise LexerError."""
        lexer = Lexer('"hello', "test.qsr")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert "unterminated string" in exc_info.value.message
    
    def test_unterminated_string_newline(self) -> None:
        """String with newline before closing quote should raise LexerError."""
        lexer = Lexer('"hello\nworld"', "test.qsr")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert "unterminated string" in exc_info.value.message


class TestUnexpectedCharacter:
    """Test unexpected character detection."""
    
    @pytest.mark.parametrize("char", ["@", "$", "^", "`", "~"])
    def test_unexpected_characters(self, char: str) -> None:
        """Unexpected characters should raise LexerError."""
        lexer = Lexer(char, "test.qsr")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert "unexpected character" in exc_info.value.message
    
    def test_single_ampersand(self) -> None:
        """Single & should raise LexerError with helpful message."""
        lexer = Lexer("a & b", "test.qsr")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert "&&" in exc_info.value.message
    
    def test_single_pipe(self) -> None:
        """Single | should raise LexerError with helpful message."""
        lexer = Lexer("a | b", "test.qsr")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert "||" in exc_info.value.message


class TestErrorLocation:
    """Test that errors have correct source location."""
    
    def test_error_at_start(self) -> None:
        """Error at start of file should have line 1, column 1."""
        lexer = Lexer("@", "test.qsr")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert exc_info.value.span.start_line == 1
        assert exc_info.value.span.start_column == 1
    
    def test_error_after_tokens(self) -> None:
        """Error after valid tokens should have correct position."""
        lexer = Lexer("let x = @", "test.qsr")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert exc_info.value.span.start_line == 1
        assert exc_info.value.span.start_column == 9
    
    def test_error_on_second_line(self) -> None:
        """Error on second line should have line 2."""
        lexer = Lexer("let x: int = 1\n@", "test.qsr")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert exc_info.value.span.start_line == 2
    
    def test_error_includes_filename(self) -> None:
        """Error should include the filename."""
        lexer = Lexer("@", "myfile.qsr")
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        assert exc_info.value.span.file == "myfile.qsr"

"""
Tests for print keyword tokenization (Phase 5).
"""

import pytest

from quasar.lexer import Lexer
from quasar.lexer.token_type import TokenType


class TestPrintKeyword:
    """Tests for print keyword recognition."""
    
    def test_print_keyword_recognized(self):
        """print should be tokenized as PRINT keyword."""
        lexer = Lexer("print")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 2  # PRINT + EOF
        assert tokens[0].type == TokenType.PRINT
        assert tokens[0].lexeme == "print"
    
    def test_print_in_statement_context(self):
        """print(42) should tokenize correctly."""
        lexer = Lexer("print(42)")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 5  # PRINT ( INT_LITERAL ) EOF
        assert tokens[0].type == TokenType.PRINT
        assert tokens[1].type == TokenType.LPAREN
        assert tokens[2].type == TokenType.INT_LITERAL
        assert tokens[2].lexeme == "42"
        assert tokens[3].type == TokenType.RPAREN
        assert tokens[4].type == TokenType.EOF
    
    def test_print_is_not_identifier(self):
        """print should NOT be tokenized as identifier."""
        lexer = Lexer("print")
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.PRINT
        assert tokens[0].type != TokenType.IDENTIFIER
    
    def test_print_is_case_sensitive(self):
        """PRINT, Print should be identifiers, not keywords."""
        lexer = Lexer("PRINT Print pRiNt")
        tokens = lexer.tokenize()
        
        # All should be identifiers (case-sensitive)
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].lexeme == "PRINT"
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].lexeme == "Print"
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].lexeme == "pRiNt"

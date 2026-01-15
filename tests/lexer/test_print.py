"""
Tests for print keyword tokenization (Phase 5 + 5.1).
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


class TestPrintSepEnd:
    """Tests for sep and end keywords (Phase 5.1)."""
    
    def test_sep_keyword_recognized(self):
        """sep should be tokenized as SEP keyword."""
        lexer = Lexer("sep")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 2  # SEP + EOF
        assert tokens[0].type == TokenType.SEP
        assert tokens[0].lexeme == "sep"
    
    def test_end_keyword_recognized(self):
        """end should be tokenized as END keyword."""
        lexer = Lexer("end")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 2  # END + EOF
        assert tokens[0].type == TokenType.END
        assert tokens[0].lexeme == "end"
    
    def test_sep_in_print_context(self):
        """print(a, sep=',') should tokenize correctly."""
        lexer = Lexer('print(a, sep=",")')
        tokens = lexer.tokenize()
        
        # PRINT ( IDENTIFIER , SEP = STRING_LITERAL ) EOF
        assert len(tokens) == 9
        assert tokens[0].type == TokenType.PRINT
        assert tokens[1].type == TokenType.LPAREN
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].lexeme == "a"
        assert tokens[3].type == TokenType.COMMA
        assert tokens[4].type == TokenType.SEP
        assert tokens[5].type == TokenType.EQUAL
        assert tokens[6].type == TokenType.STRING_LITERAL
        assert tokens[7].type == TokenType.RPAREN
        assert tokens[8].type == TokenType.EOF
    
    def test_end_in_print_context(self):
        """print(a, end='') should tokenize correctly."""
        lexer = Lexer('print(a, end="")')
        tokens = lexer.tokenize()
        
        # PRINT ( IDENTIFIER , END = STRING_LITERAL ) EOF
        assert len(tokens) == 9
        assert tokens[0].type == TokenType.PRINT
        assert tokens[4].type == TokenType.END
        assert tokens[5].type == TokenType.EQUAL
        assert tokens[6].type == TokenType.STRING_LITERAL
    
    def test_sep_and_end_together(self):
        """print(a, b, sep=',', end='!') should tokenize all keywords."""
        lexer = Lexer("print(a, b, sep=\",\", end=\"!\")")
        tokens = lexer.tokenize()
        
        # PRINT ( a , b , sep = "," , end = "!" ) EOF
        assert len(tokens) == 15
        assert tokens[0].type == TokenType.PRINT
        assert tokens[6].type == TokenType.SEP
        assert tokens[10].type == TokenType.END
    
    def test_sep_end_case_sensitive(self):
        """SEP, End, END should be identifiers (case-sensitive)."""
        lexer = Lexer("SEP End END Sep")
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].lexeme == "SEP"
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].lexeme == "End"
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].lexeme == "END"
        assert tokens[3].type == TokenType.IDENTIFIER
        assert tokens[3].lexeme == "Sep"

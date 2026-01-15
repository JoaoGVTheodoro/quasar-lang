"""
Quasar lexer module.

Converts source code into a sequence of tokens.

This module provides:
    - Lexer: The main lexer class
    - Token: A single lexical token
    - TokenType: Enumeration of token types
    - LexerError: Exception for lexical errors

Usage:
    from quasar.lexer import Lexer, LexerError
    
    try:
        lexer = Lexer(source_code, "example.qsr")
        tokens = lexer.tokenize()
    except LexerError as e:
        print(e)

Token Categories:
    Keywords (11):
        LET, CONST, FN, RETURN, IF, ELSE, WHILE, BREAK, CONTINUE, TRUE, FALSE
    
    Type Keywords (4):
        INT, FLOAT, BOOL, STR
    
    Literals (3):
        INT_LITERAL, FLOAT_LITERAL, STRING_LITERAL
    
    Arithmetic Operators (5):
        PLUS (+), MINUS (-), STAR (*), SLASH (/), PERCENT (%)
    
    Comparison Operators (6):
        EQUAL_EQUAL (==), BANG_EQUAL (!=),
        LESS (<), GREATER (>), LESS_EQUAL (<=), GREATER_EQUAL (>=)
    
    Logical Operators (3):
        AND_AND (&&), OR_OR (||), BANG (!)
    
    Assignment (1):
        EQUAL (=)
    
    Punctuation (7):
        LPAREN ((), RPAREN ()), LBRACE ({), RBRACE (}),
        COLON (:), COMMA (,), ARROW (->)
    
    Special (1):
        EOF
"""

from quasar.lexer.token_type import TokenType, KEYWORDS
from quasar.lexer.token import Token
from quasar.lexer.errors import LexerError
from quasar.lexer.lexer import Lexer

__all__ = [
    "Lexer",
    "Token",
    "TokenType",
    "LexerError",
    "KEYWORDS",
]

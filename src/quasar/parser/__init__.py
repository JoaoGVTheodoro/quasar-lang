"""
Quasar parser module.

Converts a sequence of tokens into an Abstract Syntax Tree (AST).

This module provides:
    - Parser: The main recursive descent parser
    - ParserError: Exception for syntax errors

Usage:
    from quasar.lexer import Lexer
    from quasar.parser import Parser, ParserError
    
    try:
        lexer = Lexer(source_code, "example.qsr")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
    except ParserError as e:
        print(e)

Grammar Rules Implemented (Phase 1 FROZEN):
    - program: sequence of declarations
    - declarations: let, const, fn, statements
    - statements: if, while, return, break, continue, block, assign, expr
    - expressions: binary, unary, call, literals, identifiers, grouped

Precedence (lowest to highest):
    1. ||        (logical or, left)
    2. &&        (logical and, left)
    3. == !=     (equality, left)
    4. < > <= >= (comparison, left)
    5. + -       (additive, left)
    6. * / %     (multiplicative, left)
    7. ! -       (unary, right)
    8. ()        (call, left)
"""

from quasar.parser.errors import ParserError
from quasar.parser.parser import Parser

__all__ = [
    "Parser",
    "ParserError",
]

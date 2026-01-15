"""
Quasar Lexer — Token types.

This module defines the TokenType enum representing all
valid tokens in the Quasar language.
"""

from enum import Enum, auto


class TokenType(Enum):
    """
    Enumeration of all token types in Quasar.
    
    Categories:
    - Keywords: Language reserved words
    - Type keywords: Primitive type names
    - Literals: Constant values
    - Operators: Arithmetic, comparison, logical
    - Punctuation: Delimiters and separators
    - Special: EOF and identifiers
    """
    
    # === Keywords (12) ===
    LET = auto()        # let
    CONST = auto()      # const
    FN = auto()         # fn
    RETURN = auto()     # return
    IF = auto()         # if
    ELSE = auto()       # else
    WHILE = auto()      # while
    BREAK = auto()      # break
    CONTINUE = auto()   # continue
    TRUE = auto()       # true
    FALSE = auto()      # false
    PRINT = auto()      # print (Phase 5)
    
    # === Type Keywords (4) ===
    INT = auto()        # int
    FLOAT = auto()      # float
    BOOL = auto()       # bool
    STR = auto()        # str
    
    # === Literals (4) ===
    INT_LITERAL = auto()      # e.g., 42
    FLOAT_LITERAL = auto()    # e.g., 3.14
    STRING_LITERAL = auto()   # e.g., "hello"
    # Note: true/false are keywords, not separate literal tokens
    
    # === Identifier ===
    IDENTIFIER = auto()  # e.g., myVar, _count
    
    # === Arithmetic Operators (5) ===
    PLUS = auto()       # +
    MINUS = auto()      # -
    STAR = auto()       # *
    SLASH = auto()      # /
    PERCENT = auto()    # %
    
    # === Comparison Operators (6) ===
    EQUAL_EQUAL = auto()    # ==
    BANG_EQUAL = auto()     # !=
    LESS = auto()           # <
    GREATER = auto()        # >
    LESS_EQUAL = auto()     # <=
    GREATER_EQUAL = auto()  # >=
    
    # === Logical Operators (3) ===
    AND_AND = auto()    # &&
    OR_OR = auto()      # ||
    BANG = auto()       # !
    
    # === Assignment (1) ===
    EQUAL = auto()      # =
    
    # === Punctuation (7) ===
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    COLON = auto()      # :
    COMMA = auto()      # ,
    ARROW = auto()      # ->
    
    # === Special (1) ===
    EOF = auto()        # End of file
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return f"TokenType.{self.name}"


# Mapping from keyword strings to token types
KEYWORDS: dict[str, TokenType] = {
    # Language keywords
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "fn": TokenType.FN,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "print": TokenType.PRINT,  # Phase 5
    # Type keywords
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "bool": TokenType.BOOL,
    "str": TokenType.STR,
}

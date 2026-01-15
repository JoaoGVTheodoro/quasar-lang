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
    
    # === Keywords (16) ===
    LET = auto()        # let
    CONST = auto()      # const
    FN = auto()         # fn
    RETURN = auto()     # return
    IF = auto()         # if
    ELSE = auto()       # else
    WHILE = auto()      # while
    FOR = auto()        # for (Phase 6.3)
    IN = auto()         # in (Phase 6.3)
    BREAK = auto()      # break
    CONTINUE = auto()   # continue
    TRUE = auto()       # true
    FALSE = auto()      # false
    PRINT = auto()      # print (Phase 5)
    SEP = auto()        # sep (Phase 5.1 - print separator)
    END = auto()        # end (Phase 5.1 - print terminator)
    
    STRUCT = auto()     # struct

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
    
    # === Punctuation (10) ===
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    LBRACKET = auto()   # [ (Phase 6.0)
    RBRACKET = auto()   # ] (Phase 6.0)
    COLON = auto()      # :
    COMMA = auto()      # ,
    ARROW = auto()      # ->
    DOT = auto()        # . (Phase 8.2 - member access)
    DOTDOT = auto()     # .. (Phase 6.3 - range operator)
    
    # === Special (1) ===
    EOF = auto()        # End of file
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return f"TokenType.{self.name}"


# Mapping from keyword strings to token types
KEYWORDS: dict[str, TokenType] = {
    # Language keywords
    "struct": TokenType.STRUCT,
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "fn": TokenType.FN,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,      # Phase 6.3
    "in": TokenType.IN,        # Phase 6.3
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "print": TokenType.PRINT,  # Phase 5
    "sep": TokenType.SEP,      # Phase 5.1
    "end": TokenType.END,      # Phase 5.1
    # Type keywords
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "bool": TokenType.BOOL,
    "str": TokenType.STR,
}

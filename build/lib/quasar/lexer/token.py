"""
Quasar Lexer — Token class.

This module defines the Token class representing a single
lexical token with its type, value, and source location.
"""

from dataclasses import dataclass

from quasar.ast.span import Span
from quasar.lexer.token_type import TokenType


@dataclass(frozen=True, slots=True)
class Token:
    """
    A single lexical token.
    
    Attributes:
        type: The type of this token.
        lexeme: The original source text that produced this token.
        literal: The computed value for literals (int, float, str, bool), None otherwise.
        span: The source location of this token.
    """
    
    type: TokenType
    lexeme: str
    literal: int | float | str | bool | None
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"Token("
            f"type={self.type!r}, "
            f"lexeme={self.lexeme!r}, "
            f"literal={self.literal!r}, "
            f"span={self.span!r})"
        )
    
    def __str__(self) -> str:
        """Human-readable token representation."""
        if self.literal is not None:
            return f"{self.type.name}({self.literal!r})"
        return f"{self.type.name}({self.lexeme!r})"

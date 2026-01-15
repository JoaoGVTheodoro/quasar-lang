"""
Quasar Lexer — Lexical errors.

This module defines the LexerError exception for reporting
lexical errors with source location.
"""

from dataclasses import dataclass

from quasar.ast.span import Span


@dataclass
class LexerError(Exception):
    """
    Exception raised for lexical errors.
    
    Attributes:
        message: Description of the error.
        span: Source location where the error occurred.
    """
    
    message: str
    span: Span
    
    def __str__(self) -> str:
        """Format error message with location."""
        return f"{self.span}: error: {self.message}"
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return f"LexerError(message={self.message!r}, span={self.span!r})"

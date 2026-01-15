"""
Quasar Parser — Syntax errors.

This module defines the ParserError exception for reporting
syntax errors with source location.
"""

from dataclasses import dataclass

from quasar.ast.span import Span


@dataclass
class ParserError(Exception):
    """
    Exception raised for syntax errors.
    
    Attributes:
        message: Description of the error.
        span: Source location where the error occurred.
    """
    
    message: str
    span: Span
    
    def __str__(self) -> str:
        """Format error message with location."""
        return f"{self.span}: syntax error: {self.message}"
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return f"ParserError(message={self.message!r}, span={self.span!r})"

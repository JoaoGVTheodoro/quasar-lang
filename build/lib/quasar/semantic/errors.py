"""
Semantic analysis errors.
"""

from dataclasses import dataclass
from quasar.ast import Span


@dataclass
class SemanticError(Exception):
    """
    Exception raised when a semantic error is detected.
    
    Attributes:
        code: Error code (e.g., "E0001" for undeclared variable).
        message: Human-readable error description.
        span: Source location where the error occurred.
    """
    code: str
    message: str
    span: Span
    
    def __str__(self) -> str:
        return f"{self.span.file}:{self.span.start_line}:{self.span.start_column}: {self.code}: {self.message}"

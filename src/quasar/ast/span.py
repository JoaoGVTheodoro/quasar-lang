"""
Quasar AST — Source location tracking.

This module defines the Span type used for error reporting
and source location tracking in all AST nodes.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Span:
    """
    Represents a range of source code positions.
    
    All positions are 1-indexed (first line is 1, first column is 1).
    
    Attributes:
        start_line: Starting line number (1-indexed).
        start_column: Starting column number (1-indexed).
        end_line: Ending line number (1-indexed, inclusive).
        end_column: Ending column number (1-indexed, inclusive).
        file: Source file name or path.
    """
    
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    file: str
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"Span("
            f"start_line={self.start_line}, "
            f"start_column={self.start_column}, "
            f"end_line={self.end_line}, "
            f"end_column={self.end_column}, "
            f"file={self.file!r})"
        )
    
    def __str__(self) -> str:
        """Human-readable location string."""
        if self.start_line == self.end_line:
            return f"{self.file}:{self.start_line}:{self.start_column}"
        return (
            f"{self.file}:{self.start_line}:{self.start_column}-"
            f"{self.end_line}:{self.end_column}"
        )

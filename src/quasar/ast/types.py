"""
Quasar AST — Type annotations.

This module defines the TypeAnnotation enum representing
the four primitive types in Quasar.
"""

from enum import Enum, auto


class TypeAnnotation(Enum):
    """
    Represents a type annotation in Quasar source code.
    
    Quasar has exactly four primitive types:
    - INT: Arbitrary precision integer
    - FLOAT: 64-bit floating point
    - BOOL: Boolean (true/false)
    - STR: UTF-8 string
    """
    
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    STR = auto()
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return f"TypeAnnotation.{self.name}"
    
    def __str__(self) -> str:
        """Human-readable type name (lowercase)."""
        return self.name.lower()

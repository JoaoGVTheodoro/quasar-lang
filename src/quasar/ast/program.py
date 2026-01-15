"""
Quasar AST — Program node.

This module defines the root Program node of the AST.
"""

from dataclasses import dataclass

from quasar.ast.base import Declaration, Node
from quasar.ast.span import Span


@dataclass
class Program(Node):
    """
    Program: the root node of a Quasar AST.
    
    A program is a sequence of declarations (variables, constants, functions).
    
    Example:
        const PI: float = 3.14
        
        fn main() -> int {
            return 0
        }
    
    Attributes:
        declarations: List of top-level declarations.
        span: Source location (entire file).
    """
    
    declarations: list[Declaration]
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"Program("
            f"declarations={self.declarations!r}, "
            f"span={self.span!r})"
        )

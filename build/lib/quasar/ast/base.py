"""
Quasar AST — Base node classes.

This module defines the abstract base classes for AST nodes.
All concrete nodes inherit from these bases.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from quasar.ast.span import Span


@dataclass
class Node(ABC):
    """
    Abstract base class for all AST nodes.
    
    Every node has a span indicating its source location.
    """
    
    span: Span
    
    @abstractmethod
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        pass


@dataclass
class Expression(Node, ABC):
    """
    Abstract base class for all expression nodes.
    
    Expressions are nodes that produce a value when evaluated.
    """
    
    pass


@dataclass
class Statement(Node, ABC):
    """
    Abstract base class for all statement nodes.
    
    Statements are nodes that perform an action but do not produce a value.
    """
    
    pass


@dataclass
class Declaration(Node, ABC):
    """
    Abstract base class for all declaration nodes.
    
    Declarations introduce new names into a scope.
    """
    
    pass

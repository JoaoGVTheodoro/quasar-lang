"""
Quasar AST — Type System.

This module defines the type system for Quasar, supporting both
primitive types and composite types (lists).

Phase 6.0 refactored from Enum to class hierarchy to support:
- Primitive types: int, float, bool, str, void
- List types: [T] where T is any type (recursive)
"""

from dataclasses import dataclass
from typing import Union


# =============================================================================
# Type Classes
# =============================================================================

@dataclass(frozen=True)
class PrimitiveType:
    """
    Represents a primitive type in Quasar.
    
    Primitive types: int, float, bool, str, void
    """
    name: str
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"PrimitiveType({self.name!r})"


@dataclass(frozen=True)
class ListType:
    """
    Represents a list type in Quasar: [T]
    
    The element_type can be any QuasarType, allowing nested lists:
    - [int]      -> ListType(PrimitiveType("int"))
    - [[str]]    -> ListType(ListType(PrimitiveType("str")))
    """
    element_type: "QuasarType"
    
    def __str__(self) -> str:
        return f"[{self.element_type}]"
    
    def __repr__(self) -> str:
        return f"ListType({self.element_type!r})"


# Type alias for all Quasar types
QuasarType = Union[PrimitiveType, ListType]


# =============================================================================
# Primitive Type Constants
# =============================================================================

INT = PrimitiveType("int")
FLOAT = PrimitiveType("float")
BOOL = PrimitiveType("bool")
STR = PrimitiveType("str")
VOID = PrimitiveType("void")
ANY = PrimitiveType("any")  # Opaque type for external module access (Phase 9)


# =============================================================================
# Helper Functions
# =============================================================================

def list_of(element_type: QuasarType) -> ListType:
    """Create a list type with the given element type."""
    return ListType(element_type)


def is_primitive(t: QuasarType) -> bool:
    """Check if type is a primitive type."""
    return isinstance(t, PrimitiveType)


def is_list(t: QuasarType) -> bool:
    """Check if type is a list type."""
    return isinstance(t, ListType)


# =============================================================================
# Backward Compatibility Layer
# =============================================================================

class TypeAnnotation:
    """
    Backward compatibility wrapper for the old TypeAnnotation enum.
    
    This class provides the same interface as the old Enum:
    - TypeAnnotation.INT, TypeAnnotation.FLOAT, etc.
    - Comparison with == works as expected
    
    DEPRECATED: Use INT, FLOAT, BOOL, STR, VOID directly.
    """
    INT = INT
    FLOAT = FLOAT
    BOOL = BOOL
    STR = STR
    VOID = VOID

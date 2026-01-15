"""
Quasar AST — Operators.

This module defines the BinaryOp and UnaryOp enums
representing all operators in Quasar.
"""

from enum import Enum, auto


class BinaryOp(Enum):
    """
    Represents a binary operator in Quasar.
    
    Arithmetic operators:
    - ADD: + (addition, string concatenation)
    - SUB: - (subtraction)
    - MUL: * (multiplication)
    - DIV: / (division)
    - MOD: % (modulo)
    
    Comparison operators:
    - EQ: == (equality)
    - NE: != (inequality)
    - LT: < (less than)
    - GT: > (greater than)
    - LE: <= (less than or equal)
    - GE: >= (greater than or equal)
    
    Logical operators:
    - AND: && (logical and)
    - OR: || (logical or)
    """
    
    # Arithmetic
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    
    # Comparison
    EQ = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    
    # Logical
    AND = auto()
    OR = auto()
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return f"BinaryOp.{self.name}"
    
    def __str__(self) -> str:
        """Human-readable operator symbol."""
        symbols = {
            BinaryOp.ADD: "+",
            BinaryOp.SUB: "-",
            BinaryOp.MUL: "*",
            BinaryOp.DIV: "/",
            BinaryOp.MOD: "%",
            BinaryOp.EQ: "==",
            BinaryOp.NE: "!=",
            BinaryOp.LT: "<",
            BinaryOp.GT: ">",
            BinaryOp.LE: "<=",
            BinaryOp.GE: ">=",
            BinaryOp.AND: "&&",
            BinaryOp.OR: "||",
        }
        return symbols[self]


class UnaryOp(Enum):
    """
    Represents a unary operator in Quasar.
    
    - NEG: - (numeric negation)
    - NOT: ! (logical not)
    """
    
    NEG = auto()
    NOT = auto()
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return f"UnaryOp.{self.name}"
    
    def __str__(self) -> str:
        """Human-readable operator symbol."""
        symbols = {
            UnaryOp.NEG: "-",
            UnaryOp.NOT: "!",
        }
        return symbols[self]

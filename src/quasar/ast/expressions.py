"""
Quasar AST — Expression nodes.

This module defines all expression node types:
- BinaryExpr: Binary operations (a + b, x && y, etc.)
- UnaryExpr: Unary operations (-x, !flag)
- CallExpr: Function calls (fn(a, b))
- Identifier: Variable/constant references (x, PI)
- IntLiteral: Integer literals (42)
- FloatLiteral: Float literals (3.14)
- StringLiteral: String literals ("hello")
- BoolLiteral: Boolean literals (true, false)

Note: GroupExpr does NOT exist (D2.1 — parentheses resolved by parser).
"""

from dataclasses import dataclass

from quasar.ast.base import Expression
from quasar.ast.operators import BinaryOp, UnaryOp
from quasar.ast.span import Span


@dataclass
class BinaryExpr(Expression):
    """
    Binary expression: left operator right.
    
    Examples:
        a + b
        x > 0 && x < 100
        total == expected
    
    Attributes:
        left: Left operand expression.
        operator: Binary operator.
        right: Right operand expression.
        span: Source location.
    """
    
    left: Expression
    operator: BinaryOp
    right: Expression
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"BinaryExpr("
            f"left={self.left!r}, "
            f"operator={self.operator!r}, "
            f"right={self.right!r}, "
            f"span={self.span!r})"
        )


@dataclass
class UnaryExpr(Expression):
    """
    Unary expression: operator operand.
    
    Examples:
        -x
        !flag
    
    Attributes:
        operator: Unary operator.
        operand: Operand expression.
        span: Source location.
    """
    
    operator: UnaryOp
    operand: Expression
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"UnaryExpr("
            f"operator={self.operator!r}, "
            f"operand={self.operand!r}, "
            f"span={self.span!r})"
        )


@dataclass
class CallExpr(Expression):
    """
    Function call expression: callee(arguments).
    
    Examples:
        add(1, 2)
        print("hello")
        max(a, b)
    
    Attributes:
        callee: Name of the function being called.
        arguments: List of argument expressions.
        span: Source location.
    """
    
    callee: str
    arguments: list[Expression]
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"CallExpr("
            f"callee={self.callee!r}, "
            f"arguments={self.arguments!r}, "
            f"span={self.span!r})"
        )


@dataclass
class Identifier(Expression):
    """
    Identifier expression: a reference to a variable or constant.
    
    Examples:
        x
        PI
        counter
    
    Attributes:
        name: The identifier name.
        span: Source location.
    """
    
    name: str
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"Identifier("
            f"name={self.name!r}, "
            f"span={self.span!r})"
        )


@dataclass
class IntLiteral(Expression):
    """
    Integer literal expression.
    
    Examples:
        0
        42
        1000000
    
    Attributes:
        value: The integer value.
        span: Source location.
    """
    
    value: int
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"IntLiteral("
            f"value={self.value!r}, "
            f"span={self.span!r})"
        )


@dataclass
class FloatLiteral(Expression):
    """
    Float literal expression.
    
    Examples:
        3.14
        0.5
        100.0
    
    Attributes:
        value: The float value.
        span: Source location.
    """
    
    value: float
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"FloatLiteral("
            f"value={self.value!r}, "
            f"span={self.span!r})"
        )


@dataclass
class StringLiteral(Expression):
    """
    String literal expression.
    
    Examples:
        "hello"
        ""
        "hello world"
    
    Attributes:
        value: The string value (without quotes).
        span: Source location.
    """
    
    value: str
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"StringLiteral("
            f"value={self.value!r}, "
            f"span={self.span!r})"
        )


@dataclass
class BoolLiteral(Expression):
    """
    Boolean literal expression.
    
    Examples:
        true
        false
    
    Attributes:
        value: The boolean value.
        span: Source location.
    """
    
    value: bool
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"BoolLiteral("
            f"value={self.value!r}, "
            f"span={self.span!r})"
        )


@dataclass
class ListLiteral(Expression):
    """
    List literal expression (Phase 6.0).
    
    Examples:
        []
        [1, 2, 3]
        ["a", "b", "c"]
        [[1, 2], [3, 4]]
    
    Attributes:
        elements: List of element expressions.
        span: Source location.
    """
    
    elements: list[Expression]
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"ListLiteral("
            f"elements={self.elements!r}, "
            f"span={self.span!r})"
        )


@dataclass
class IndexExpr(Expression):
    """
    Index access expression (Phase 6.1).
    
    Examples:
        list[0]
        matrix[i][j]
        arr[1 + 1]
    
    Attributes:
        target: The expression being indexed (list).
        index: The index expression (must be int at runtime).
        span: Source location.
    """
    
    target: Expression
    index: Expression
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"IndexExpr("
            f"target={self.target!r}, "
            f"index={self.index!r}, "
            f"span={self.span!r})"
        )


@dataclass
class RangeExpr(Expression):
    """
    Range expression (Phase 6.3).
    
    Examples:
        0..10
        start..end
        1..n+1
    
    Note: Ranges are exclusive on the end (like Python range).
    
    Attributes:
        start: The starting value expression (must be int).
        end: The ending value expression (must be int, exclusive).
        span: Source location.
    """
    
    start: Expression
    end: Expression
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"RangeExpr("
            f"start={self.start!r}, "
            f"end={self.end!r}, "
            f"span={self.span!r})"
        )


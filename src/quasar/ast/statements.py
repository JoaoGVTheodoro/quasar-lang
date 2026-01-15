"""
Quasar AST — Statement nodes.

This module defines all statement node types:
- ExpressionStmt: Expression used as statement
- IfStmt: Conditional statement
- WhileStmt: Loop statement
- ReturnStmt: Function return
- BreakStmt: Loop break
- ContinueStmt: Loop continue
- AssignStmt: Variable assignment
- PrintStmt: Print statement (Phase 5)
- Block: Block of declarations
"""

from dataclasses import dataclass

from quasar.ast.base import Declaration, Expression, Statement
from quasar.ast.span import Span


@dataclass
class Block(Statement):
    """
    Block statement: a sequence of declarations enclosed in braces.
    
    Examples:
        { let x: int = 1 }
        { x = x + 1 }
    
    Attributes:
        declarations: List of declarations in the block.
        span: Source location.
    """
    
    declarations: list[Declaration]
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"Block("
            f"declarations={self.declarations!r}, "
            f"span={self.span!r})"
        )


@dataclass
class ExpressionStmt(Statement):
    """
    Expression statement: an expression used as a statement.
    
    Examples:
        add(1, 2)
        x + y
    
    Attributes:
        expression: The expression.
        span: Source location.
    """
    
    expression: Expression
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"ExpressionStmt("
            f"expression={self.expression!r}, "
            f"span={self.span!r})"
        )


@dataclass
class IfStmt(Statement):
    """
    If statement: conditional execution.
    
    Examples:
        if x > 0 { return x }
        if flag { a = 1 } else { a = 0 }
    
    Attributes:
        condition: Condition expression (must be bool).
        then_block: Block to execute if condition is true.
        else_block: Optional block to execute if condition is false.
        span: Source location.
    """
    
    condition: Expression
    then_block: Block
    else_block: Block | None
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"IfStmt("
            f"condition={self.condition!r}, "
            f"then_block={self.then_block!r}, "
            f"else_block={self.else_block!r}, "
            f"span={self.span!r})"
        )


@dataclass
class WhileStmt(Statement):
    """
    While statement: loop execution.
    
    Examples:
        while i < 10 { i = i + 1 }
        while true { break }
    
    Attributes:
        condition: Condition expression (must be bool).
        body: Block to execute while condition is true.
        span: Source location.
    """
    
    condition: Expression
    body: Block
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"WhileStmt("
            f"condition={self.condition!r}, "
            f"body={self.body!r}, "
            f"span={self.span!r})"
        )


@dataclass
class ReturnStmt(Statement):
    """
    Return statement: return a value from a function.
    
    Examples:
        return 42
        return x + y
    
    Note: Return always requires a value (no void functions).
    
    Attributes:
        value: Expression to return.
        span: Source location.
    """
    
    value: Expression
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"ReturnStmt("
            f"value={self.value!r}, "
            f"span={self.span!r})"
        )


@dataclass
class BreakStmt(Statement):
    """
    Break statement: exit the innermost loop.
    
    Example:
        break
    
    Note: Only valid inside a while loop.
    
    Attributes:
        span: Source location.
    """
    
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return f"BreakStmt(span={self.span!r})"


@dataclass
class ContinueStmt(Statement):
    """
    Continue statement: skip to next iteration of innermost loop.
    
    Example:
        continue
    
    Note: Only valid inside a while loop.
    
    Attributes:
        span: Source location.
    """
    
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return f"ContinueStmt(span={self.span!r})"


@dataclass
class AssignStmt(Statement):
    """
    Assignment statement: assign a value to a variable.
    
    Examples:
        x = 42
        total = total + 1
    
    Note: Target must be a variable declared with 'let' (not const).
    
    Attributes:
        target: Name of the variable to assign to.
        value: Expression to assign.
        span: Source location.
    """
    
    target: str
    value: Expression
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"AssignStmt("
            f"target={self.target!r}, "
            f"value={self.value!r}, "
            f"span={self.span!r})"
        )


@dataclass
class PrintStmt(Statement):
    """
    Print statement: output values to console (Phase 5 + 5.1).
    
    Examples:
        print(42)
        print("hello")
        print(x + y)
        print(a, b, c)                    # Multiple arguments
        print(a, b, sep=", ")             # Custom separator
        print(a, end="")                  # No newline
        print(a, b, sep="-", end="!\n")   # Both sep and end
    
    Note: print is a statement, not an expression. It cannot be
    used as a value (e.g., let x = print(1) is invalid).
    
    Attributes:
        arguments: List of expressions to print (at least 1).
        sep: Optional separator expression (must be str).
        end: Optional end expression (must be str).
        span: Source location.
    """
    
    arguments: list[Expression]
    sep: Expression | None
    end: Expression | None
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"PrintStmt("
            f"arguments={self.arguments!r}, "
            f"sep={self.sep!r}, "
            f"end={self.end!r}, "
            f"span={self.span!r})"
        )

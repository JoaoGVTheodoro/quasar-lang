"""
Quasar AST module.

Defines the Abstract Syntax Tree node types for the Quasar language.

This module provides the complete AST hierarchy:

Base classes:
    - Node: Abstract base for all nodes
    - Expression: Abstract base for expressions
    - Statement: Abstract base for statements
    - Declaration: Abstract base for declarations

Location:
    - Span: Source location tracking

Types:
    - TypeAnnotation: Enum of primitive types (INT, FLOAT, BOOL, STR)

Operators:
    - BinaryOp: Enum of binary operators
    - UnaryOp: Enum of unary operators

Expressions:
    - BinaryExpr: Binary operations (a + b)
    - UnaryExpr: Unary operations (-x, !flag)
    - CallExpr: Function calls (fn(args))
    - Identifier: Variable references (x)
    - IntLiteral: Integer literals (42)
    - FloatLiteral: Float literals (3.14)
    - StringLiteral: String literals ("hello")
    - BoolLiteral: Boolean literals (true, false)

Statements:
    - Block: Block of declarations ({ ... })
    - ExpressionStmt: Expression as statement
    - IfStmt: Conditional (if/else)
    - WhileStmt: Loop (while)
    - ReturnStmt: Function return
    - BreakStmt: Loop break
    - ContinueStmt: Loop continue
    - AssignStmt: Variable assignment
    - PrintStmt: Print output (Phase 5)

Declarations:
    - Param: Function parameter
    - VarDecl: Variable declaration (let)
    - ConstDecl: Constant declaration (const)
    - FnDecl: Function declaration (fn)

Program:
    - Program: Root node
"""

# Location
from quasar.ast.span import Span

# Types
from quasar.ast.types import (
    TypeAnnotation,
    QuasarType,
    PrimitiveType,
    ListType,
    DictType,
    INT,
    FLOAT,
    BOOL,
    STR,
    VOID,
    ANY,
    list_of,
    is_primitive,
    is_list,
    is_dict,
    is_hashable,
)

# Operators
from quasar.ast.operators import BinaryOp, UnaryOp

# Base classes
from quasar.ast.base import Node, Expression, Statement, Declaration

# Expressions
from quasar.ast.expressions import (
    BinaryExpr,
    UnaryExpr,
    CallExpr,
    Identifier,
    IntLiteral,
    FloatLiteral,
    StringLiteral,
    BoolLiteral,
    ListLiteral,
    IndexExpr,
    RangeExpr,
    FieldInit,
    StructInitExpr,
    MemberAccessExpr,
    DictEntry,
    DictLiteral,
    MethodCallExpr,
)

# Statements
from quasar.ast.statements import (
    Block,
    ExpressionStmt,
    IfStmt,
    WhileStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    AssignStmt,
    PrintStmt,
    IndexAssignStmt,
    ForStmt,
    MemberAssignStmt,
)

# Declarations
from quasar.ast.declarations import (
    Param,
    VarDecl,
    ConstDecl,
    FnDecl,
    StructDecl,
    ImportDecl,
    StructField,
)

# Program
from quasar.ast.program import Program

__all__ = [
    # Location
    "Span",
    # Types
    "TypeAnnotation",
    # Operators
    "BinaryOp",
    "UnaryOp",
    # Base classes
    "Node",
    "Expression",
    "Statement",
    "Declaration",
    # Expressions
    "BinaryExpr",
    "UnaryExpr",
    "CallExpr",
    "Identifier",
    "IntLiteral",
    "FloatLiteral",
    "StringLiteral",
    "BoolLiteral",
    "ListLiteral",
    "IndexExpr",
    "RangeExpr",
    "FieldInit",
    "StructInitExpr",
    "MemberAccessExpr",
    "DictEntry",
    "DictLiteral",
    "MethodCallExpr",
    # Statements
    "Block",
    "ExpressionStmt",
    "IfStmt",
    "WhileStmt",
    "ReturnStmt",
    "BreakStmt",
    "ContinueStmt",
    "AssignStmt",
    "PrintStmt",
    "IndexAssignStmt",
    "ForStmt",
    "MemberAssignStmt",
    # Declarations
    "Param",
    "VarDecl",
    "ConstDecl",
    "FnDecl",
    "StructDecl",
    "ImportDecl",
    "StructField",
    # Program
    "Program",
]

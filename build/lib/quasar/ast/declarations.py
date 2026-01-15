"""
Quasar AST — Declaration nodes.

This module defines all declaration node types:
- VarDecl: Variable declaration (let)
- ConstDecl: Constant declaration (const)
- FnDecl: Function declaration (fn)
- Param: Function parameter
"""

from dataclasses import dataclass

from quasar.ast.base import Declaration, Expression
from quasar.ast.span import Span
from quasar.ast.statements import Block
from quasar.ast.types import TypeAnnotation


@dataclass
class Param:
    """
    Function parameter.
    
    Example:
        x: int
    
    Attributes:
        name: Parameter name.
        type_annotation: Parameter type.
        span: Source location.
    """
    
    name: str
    type_annotation: TypeAnnotation
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"Param("
            f"name={self.name!r}, "
            f"type_annotation={self.type_annotation!r}, "
            f"span={self.span!r})"
        )


@dataclass
class VarDecl(Declaration):
    """
    Variable declaration: let name: type = initializer.
    
    Example:
        let x: int = 42
    
    Attributes:
        name: Variable name.
        type_annotation: Variable type.
        initializer: Initial value expression.
        span: Source location.
    """
    
    name: str
    type_annotation: TypeAnnotation
    initializer: Expression
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"VarDecl("
            f"name={self.name!r}, "
            f"type_annotation={self.type_annotation!r}, "
            f"initializer={self.initializer!r}, "
            f"span={self.span!r})"
        )


@dataclass
class ConstDecl(Declaration):
    """
    Constant declaration: const name: type = initializer.
    
    Example:
        const PI: float = 3.14159
    
    Attributes:
        name: Constant name.
        type_annotation: Constant type.
        initializer: Value expression.
        span: Source location.
    """
    
    name: str
    type_annotation: TypeAnnotation
    initializer: Expression
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"ConstDecl("
            f"name={self.name!r}, "
            f"type_annotation={self.type_annotation!r}, "
            f"initializer={self.initializer!r}, "
            f"span={self.span!r})"
        )


@dataclass
class FnDecl(Declaration):
    """
    Function declaration: fn name(params) -> return_type { body }.
    
    Example:
        fn add(a: int, b: int) -> int {
            return a + b
        }
    
    Attributes:
        name: Function name.
        params: List of parameters.
        return_type: Return type annotation.
        body: Function body block.
        span: Source location.
    """
    
    name: str
    params: list[Param]
    return_type: TypeAnnotation
    body: Block
    span: Span
    
    def __repr__(self) -> str:
        """Deterministic representation for snapshots."""
        return (
            f"FnDecl("
            f"name={self.name!r}, "
            f"params={self.params!r}, "
            f"return_type={self.return_type!r}, "
            f"body={self.body!r}, "
            f"span={self.span!r})"
        )

@dataclass
class StructField:
    """
    Field Definition in a Struct.

    Example:
        name: str

    Attributes:
        name: Field name.
        type_annotation: Field type.
        span: Source location.
    """
    name: str
    type_annotation: TypeAnnotation
    span: Span

    def __repr__(self) -> str:
        return (
            f"StructField("
            f"name={self.name!r}, "
            f"type_annotation={self.type_annotation!r}, "
            f"span={self.span!r})"
        )


@dataclass
class StructDecl(Declaration):
    """
    Struct Declaration: struct Name { fields }

    Example:
        struct User {
            name: str,
            age: int
        }

    Attributes:
        name: Struct name.
        fields: List of fields.
        span: Source location.
    """
    name: str
    fields: list[StructField]
    span: Span

    def __repr__(self) -> str:
        return (
            f"StructDecl("
            f"name={self.name!r}, "
            f"fields={self.fields!r}, "
            f"span={self.span!r})"
        )

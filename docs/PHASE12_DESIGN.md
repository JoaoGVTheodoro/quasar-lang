# Phase 12 — Enums Design Document

**Status:** PROPOSAL (Awaiting Freeze)  
**Version:** 1.0.0  
**Date:** 2026-01-16  
**Author:** Quasar Team  
**Depends On:** Phase 11 (FROZEN, v1.8.0)  
**Target Release:** v1.9.0

---

## 1. Executive Summary

Phase 12 introduces **Enums** (Enumerated Types) — a way to define types with a fixed set of named values. This is the first step toward algebraic data types in Quasar.

**Key Features:**
- Simple enums with named variants (no payload initially)
- Enum type annotation in variable declarations
- Enum variant access via `EnumName.Variant` syntax
- Equality comparison (`==`, `!=`)

**Out of Scope (deferred to future phases):**
- Enum variants with payloads (`Ok(T)`, `Err(str)`)
- Pattern matching (`match` expressions)
- Generic enums (`Result[T, E]`)
- Enum methods

---

## 2. Syntax Specification

### 2.1 Enum Declaration

```quasar
enum Color {
    Red,
    Green,
    Blue
}

enum Status {
    Pending,
    Active,
    Completed,
    Failed
}

enum Direction {
    North,
    East,
    South,
    West
}
```

**Rules:**
- Keyword `enum` followed by PascalCase name
- Variants listed inside `{ }`, separated by commas
- Trailing comma is optional
- At least one variant required (empty enums disallowed)
- Variant names must be unique within the enum

### 2.2 Enum Type Annotation

```quasar
let color: Color = Color.Red
let direction: Direction = Direction.North
const DEFAULT_STATUS: Status = Status.Pending
```

### 2.3 Enum Access

```quasar
let c: Color = Color.Blue     // Access variant via EnumName.Variant
let d: Direction = Direction.East
```

### 2.4 Enum in Expressions

```quasar
// Equality comparison
if color == Color.Red {
    print("It's red!")
}

if status != Status.Failed {
    print("Not failed")
}

// Function parameter and return
fn next_status(current: Status) -> Status {
    if current == Status.Pending {
        return Status.Active
    }
    return Status.Completed
}
```

---

## 3. Grammar Rules (EBNF)

```ebnf
declaration    → varDecl
               | constDecl
               | fnDecl
               | structDecl
               | enumDecl          # NEW
               | importDecl
               | statement

enumDecl       → "enum" IDENTIFIER "{" enumVariants "}"

enumVariants   → enumVariant ("," enumVariant)* ","?

enumVariant    → IDENTIFIER

type           → primitiveType
               | listType
               | dictType
               | structType
               | enumType          # Enums are valid types

enumType       → IDENTIFIER        # Same as struct (user-defined type)

primary        → INT
               | FLOAT
               | STRING
               | "true"
               | "false"
               | IDENT
               | enumAccess        # NEW
               | "(" expression ")"

enumAccess     → IDENTIFIER "." IDENTIFIER   # EnumName.Variant
```

**Note:** `enumAccess` syntax overlaps with `MemberAccessExpr`. The parser must distinguish:
- If `IDENT` before `.` is a known enum type → `EnumAccessExpr`
- If `IDENT` before `.` is a variable → `MemberAccessExpr`

This requires semantic context during parsing OR deferred resolution in semantic analysis.

---

## 4. AST Additions

### 4.1 New Declaration Node

```python
# In quasar/ast/declarations.py

@dataclass
class EnumVariant:
    """
    A single variant in an enum declaration.
    
    Example:
        Red
    
    Attributes:
        name: Variant name.
        span: Source location.
    """
    name: str
    span: Span

    def __repr__(self) -> str:
        return (
            f"EnumVariant("
            f"name={self.name!r}, "
            f"span={self.span!r})"
        )


@dataclass
class EnumDecl(Declaration):
    """
    Enum declaration: enum Name { Variant1, Variant2, ... }
    
    Example:
        enum Color {
            Red,
            Green,
            Blue
        }
    
    Attributes:
        name: Enum type name.
        variants: List of variant definitions.
        span: Source location.
    """
    name: str
    variants: list[EnumVariant]
    span: Span

    def __repr__(self) -> str:
        return (
            f"EnumDecl("
            f"name={self.name!r}, "
            f"variants={self.variants!r}, "
            f"span={self.span!r})"
        )
```

### 4.2 New Expression Node

```python
# In quasar/ast/expressions.py

@dataclass
class EnumAccessExpr(Expression):
    """
    Enum variant access expression: EnumName.Variant
    
    Examples:
        Color.Red
        Status.Pending
    
    Attributes:
        enum_name: Name of the enum type.
        variant: Name of the variant.
        span: Source location.
    """
    enum_name: str
    variant: str
    span: Span

    def __repr__(self) -> str:
        return (
            f"EnumAccessExpr("
            f"enum_name={self.enum_name!r}, "
            f"variant={self.variant!r}, "
            f"span={self.span!r})"
        )
```

### 4.3 Type System Extension

```python
# In quasar/ast/types.py

@dataclass
class EnumType(QuasarType):
    """
    Enum type reference.
    
    Attributes:
        name: Name of the enum (e.g., "Color", "Status").
    """
    name: str
    
    def __repr__(self) -> str:
        return self.name
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, EnumType):
            return self.name == other.name
        return False
    
    def __hash__(self) -> int:
        return hash(("enum", self.name))
```

---

## 5. Parser Changes

### 5.1 Token Requirements

No new tokens needed. Uses existing:
- `ENUM` keyword (must be added to lexer)
- `IDENTIFIER`
- `LBRACE`, `RBRACE`
- `COMMA`
- `DOT`

### 5.2 Lexer Addition

Add `ENUM` to keyword table:

```python
# In quasar/lexer/token_type.py
class TokenType(Enum):
    # ... existing tokens ...
    ENUM = auto()  # NEW

# In quasar/lexer/lexer.py - KEYWORDS dict
KEYWORDS = {
    # ... existing keywords ...
    "enum": TokenType.ENUM,  # NEW
}
```

### 5.3 Parser Methods

```python
# In quasar/parser/parser.py

def _declaration(self) -> Declaration:
    """Parse a declaration."""
    if self._match(TokenType.LET):
        return self._var_decl()
    elif self._match(TokenType.CONST):
        return self._const_decl()
    elif self._match(TokenType.FN):
        return self._fn_decl()
    elif self._match(TokenType.STRUCT):
        return self._struct_decl()
    elif self._match(TokenType.ENUM):       # NEW
        return self._enum_decl()            # NEW
    elif self._match(TokenType.IMPORT):
        return self._import_decl()
    else:
        return self._statement()


def _enum_decl(self) -> EnumDecl:
    """
    Parse enum declaration.
    
    enumDecl → "enum" IDENTIFIER "{" enumVariants "}"
    """
    start_span = self._previous().span
    
    # Enum name
    name_token = self._consume(TokenType.IDENTIFIER, "expected enum name")
    name = name_token.lexeme
    
    # Opening brace
    self._consume(TokenType.LBRACE, "expected '{' after enum name")
    
    # Parse variants
    variants: list[EnumVariant] = []
    
    if not self._check(TokenType.RBRACE):
        # At least one variant
        variants.append(self._enum_variant())
        
        while self._match(TokenType.COMMA):
            # Allow trailing comma
            if self._check(TokenType.RBRACE):
                break
            variants.append(self._enum_variant())
    
    # Closing brace
    rbrace = self._consume(TokenType.RBRACE, "expected '}' after enum variants")
    
    # Validate at least one variant
    if len(variants) == 0:
        raise self._error("enum must have at least one variant")
    
    return EnumDecl(
        name=name,
        variants=variants,
        span=self._merge_spans(start_span, rbrace.span),
    )


def _enum_variant(self) -> EnumVariant:
    """
    Parse a single enum variant.
    
    enumVariant → IDENTIFIER
    """
    token = self._consume(TokenType.IDENTIFIER, "expected variant name")
    return EnumVariant(
        name=token.lexeme,
        span=token.span,
    )
```

### 5.4 Enum Access Parsing

The `EnumName.Variant` syntax uses the same `.` operator as member access. Two approaches:

**Option A: Parse as MemberAccessExpr, resolve in semantic analysis**
- Keep parser simple
- Semantic analyzer converts `MemberAccessExpr` on enum types to `EnumAccessExpr`

**Option B: Lookahead in parser (type tracking)**
- More complex parser
- Cleaner AST

**Recommendation:** Option A (simpler implementation).

The parser continues to produce `MemberAccessExpr` for `Color.Red`. The semantic analyzer, which knows `Color` is an enum, interprets this correctly.

---

## 6. Semantic Analysis Changes

### 6.1 Enum Type Registry

```python
# In SemanticAnalyzer.__init__
def __init__(self) -> None:
    # ... existing fields ...
    # Store enum definitions: name -> list of variant names
    self._defined_enums: dict[str, list[str]] = {}
```

### 6.2 Enum Declaration Analysis

```python
def _analyze_enum_decl(self, decl: EnumDecl) -> None:
    """
    Analyze enum declaration.
    
    Checks:
    - E1200: No redeclaration of enum name
    - E1201: No duplicate variant names within enum
    """
    # Check for name collision with existing types
    if decl.name in self._defined_types:
        raise SemanticError(
            code="E1200",
            message=f"redeclaration of type '{decl.name}'",
            span=decl.span,
        )
    if decl.name in self._defined_enums:
        raise SemanticError(
            code="E1200",
            message=f"redeclaration of enum '{decl.name}'",
            span=decl.span,
        )
    
    # Check for duplicate variants
    seen_variants: set[str] = set()
    for variant in decl.variants:
        if variant.name in seen_variants:
            raise SemanticError(
                code="E1201",
                message=f"duplicate variant '{variant.name}' in enum '{decl.name}'",
                span=variant.span,
            )
        seen_variants.add(variant.name)
    
    # Register enum
    self._defined_enums[decl.name] = [v.name for v in decl.variants]
```

### 6.3 Enum Access Type Resolution

When analyzing `MemberAccessExpr`:

```python
def _get_member_access_expr_type(self, expr: MemberAccessExpr) -> QuasarType:
    """Handle member access, including enum variant access."""
    
    # Check if this is an enum access (e.g., Color.Red)
    if isinstance(expr.object, Identifier):
        potential_enum = expr.object.name
        if potential_enum in self._defined_enums:
            # This is an enum access
            variants = self._defined_enums[potential_enum]
            if expr.member not in variants:
                raise SemanticError(
                    code="E1202",
                    message=f"enum '{potential_enum}' has no variant '{expr.member}'",
                    span=expr.span,
                )
            return EnumType(potential_enum)
    
    # Otherwise, treat as struct member access (existing logic)
    # ...
```

### 6.4 Type Annotation Resolution

Update `_resolve_type_annotation` to recognize enum types:

```python
def _resolve_type_annotation(self, type_ann) -> QuasarType:
    """Resolve type annotation, including enum types."""
    # ... existing primitive/list/dict handling ...
    
    # Check if it's a struct type
    if isinstance(type_ann, str):
        if type_ann in self._defined_types:
            return StructType(type_ann)
        if type_ann in self._defined_enums:
            return EnumType(type_ann)
        raise SemanticError(
            code="E1203",
            message=f"unknown type '{type_ann}'",
            span=...,
        )
```

### 6.5 Comparison Rules

Enums support `==` and `!=` only:

```python
def _get_binary_expr_type(self, expr: BinaryExpr) -> QuasarType:
    # ... existing logic ...
    
    # Enum comparison (equality only)
    if isinstance(left_type, EnumType) and isinstance(right_type, EnumType):
        if left_type != right_type:
            raise SemanticError(
                code="E1204",
                message=f"cannot compare enum '{left_type}' with '{right_type}'",
                span=expr.span,
            )
        if expr.operator not in (BinaryOp.EQ, BinaryOp.NE):
            raise SemanticError(
                code="E1205",
                message=f"enum types only support '==' and '!=' comparison",
                span=expr.span,
            )
        return BOOL
```

---

## 7. Code Generation

### 7.1 Strategy: Python Enum from stdlib

Quasar enums map to Python's `enum.Enum`:

```quasar
enum Color {
    Red,
    Green,
    Blue
}
```

→

```python
from enum import Enum

class Color(Enum):
    Red = "Red"
    Green = "Green"
    Blue = "Blue"
```

### 7.2 Generator Implementation

```python
# In quasar/codegen/generator.py

def __init__(self) -> None:
    # ... existing fields ...
    self._needs_enum_import = False


def generate(self, program: Program) -> str:
    # ... existing setup ...
    
    # Check if enum import is needed
    if any(isinstance(d, EnumDecl) for d in program.declarations):
        self._needs_enum_import = True
    
    # Add imports
    imports = []
    if self._needs_enum_import:
        imports.append("from enum import Enum")
    if any(isinstance(d, StructDecl) for d in program.declarations):
        imports.append("from dataclasses import dataclass")
    
    if imports:
        self._lines.extend(imports)
        self._lines.append("")
    
    # ... rest of generation ...


def _generate_enum_decl(self, decl: EnumDecl) -> None:
    """
    Generate:
    class Color(Enum):
        Red = "Red"
        Green = "Green"
        Blue = "Blue"
    """
    self._emit(f"class {decl.name}(Enum):")
    
    self._indent_level += 1
    for variant in decl.variants:
        # Use string values for simplicity
        self._emit(f'{variant.name} = "{variant.name}"')
    self._indent_level -= 1


def _generate_enum_access_expr(self, enum_name: str, variant: str) -> str:
    """Generate: EnumName.Variant"""
    return f"{enum_name}.{variant}"
```

### 7.3 Member Access Handling

Since we parse `Color.Red` as `MemberAccessExpr`, codegen handles it naturally:

```python
def _generate_member_access_expr(self, expr: MemberAccessExpr) -> str:
    """Generate member access: obj.field"""
    obj = self._generate_expression(expr.object)
    return f"{obj}.{expr.member}"
```

This already produces `Color.Red` correctly.

---

## 8. Error Codes

| Code  | Description                                |
| ----- | ------------------------------------------ |
| E1200 | Redeclaration of type name (enum or struct)|
| E1201 | Duplicate variant name within enum         |
| E1202 | Unknown variant for enum type              |
| E1203 | Unknown type name                          |
| E1204 | Cannot compare different enum types        |
| E1205 | Invalid operator for enum (not == or !=)   |
| E1206 | Empty enum (no variants)                   |

---

## 9. Test Plan

### 9.1 Lexer Tests (~5 tests)

Location: `tests/phase12/test_phase12_0_lexer.py`

| Test                        | Description                    |
| --------------------------- | ------------------------------ |
| `test_enum_keyword`         | Tokenize `enum` keyword        |
| `test_enum_decl_tokens`     | Full enum declaration tokens   |
| `test_enum_access_tokens`   | `Color.Red` token sequence     |
| `test_enum_multiple_tokens` | Multiple enums in source       |
| `test_enum_with_trailing_comma` | Trailing comma handling    |

### 9.2 Parser Tests (~12 tests)

Location: `tests/phase12/test_phase12_0_parser.py`

| Test                           | Description                        |
| ------------------------------ | ---------------------------------- |
| `test_simple_enum`             | Parse `enum Color { Red }`         |
| `test_enum_multiple_variants`  | Parse enum with 3+ variants        |
| `test_enum_trailing_comma`     | Parse with trailing comma          |
| `test_enum_no_trailing_comma`  | Parse without trailing comma       |
| `test_enum_access_in_expr`     | Parse `Color.Red` in expression    |
| `test_enum_in_var_decl`        | Parse `let c: Color = Color.Red`   |
| `test_enum_in_fn_param`        | Parse enum as function parameter   |
| `test_enum_in_fn_return`       | Parse enum as function return type |
| `test_error_empty_enum`        | Error on `enum E {}`               |
| `test_error_missing_lbrace`    | Error on `enum E Red`              |
| `test_error_missing_rbrace`    | Error on `enum E { Red`            |
| `test_error_missing_name`      | Error on `enum { Red }`            |

### 9.3 Semantic Tests (~18 tests)

Location: `tests/phase12/test_phase12_1_semantic.py`

| Test                              | Description                          |
| --------------------------------- | ------------------------------------ |
| `test_enum_decl_valid`            | Enum declaration registers type      |
| `test_enum_access_valid`          | `Color.Red` has type `Color`         |
| `test_enum_var_decl`              | Variable with enum type              |
| `test_enum_const_decl`            | Constant with enum type              |
| `test_enum_fn_param`              | Function parameter with enum type    |
| `test_enum_fn_return`             | Function return enum type            |
| `test_enum_equality_same`         | `Color.Red == Color.Red` is valid    |
| `test_enum_inequality`            | `Color.Red != Color.Blue` is valid   |
| `test_error_redecl_enum`          | E1200: Duplicate enum name           |
| `test_error_enum_struct_conflict` | E1200: Enum name conflicts with struct|
| `test_error_duplicate_variant`    | E1201: Same variant twice            |
| `test_error_unknown_variant`      | E1202: `Color.Purple` invalid        |
| `test_error_compare_diff_enums`   | E1204: `Color.Red == Status.Active`  |
| `test_error_enum_lt`              | E1205: `Color.Red < Color.Blue`      |
| `test_error_enum_gt`              | E1205: `Color.Red > Color.Blue`      |
| `test_error_enum_arithmetic`      | Error: `Color.Red + Color.Blue`      |
| `test_error_assign_wrong_enum`    | E0100: `let c: Color = Status.Active`|
| `test_error_unknown_enum_type`    | E1203: `let x: Unknown = ...`        |

### 9.4 Codegen Tests (~10 tests)

Location: `tests/phase12/test_phase12_2_codegen.py`

| Test                          | Description                         |
| ----------------------------- | ----------------------------------- |
| `test_enum_decl_codegen`      | Generates Python Enum class         |
| `test_enum_import_added`      | `from enum import Enum` is added    |
| `test_enum_access_codegen`    | `Color.Red` → `Color.Red`           |
| `test_enum_var_decl_codegen`  | Variable assignment with enum       |
| `test_enum_comparison_codegen`| Comparison expression output        |
| `test_enum_fn_codegen`        | Function with enum params/return    |
| `test_enum_multiple_codegen`  | Multiple enums in one file          |
| `test_enum_mixed_struct`      | Enum + Struct in same file          |
| `test_enum_in_condition`      | If statement with enum comparison   |
| `test_enum_in_struct_field`   | Struct field with enum type         |

### 9.5 E2E Integration Tests (~10 tests)

Location: `tests/phase12/test_phase12_3_integration.py`

| Test                           | Description                        |
| ------------------------------ | ---------------------------------- |
| `test_simple_enum_program`     | Full compile + run                 |
| `test_enum_in_function`        | Function using enum                |
| `test_enum_equality_runtime`   | Runtime equality checks            |
| `test_enum_in_if_condition`    | If branching on enum               |
| `test_enum_in_while_loop`      | While with enum state              |
| `test_enum_as_struct_field`    | Struct containing enum field       |
| `test_multiple_enums`          | Program with multiple enums        |
| `test_enum_fn_chain`           | Passing enum between functions     |
| `test_enum_print`              | Print enum value                   |
| `test_enum_state_machine`      | State machine pattern with enum    |

### 9.6 Test Execution Commands

```bash
# Run all Phase 12 tests
pytest tests/phase12/ -v

# Run specific sub-phase
pytest tests/phase12/test_phase12_0_lexer.py -v
pytest tests/phase12/test_phase12_0_parser.py -v
pytest tests/phase12/test_phase12_1_semantic.py -v
pytest tests/phase12/test_phase12_2_codegen.py -v
pytest tests/phase12/test_phase12_3_integration.py -v

# Run full test suite (ensure no regression)
pytest tests/ -v
```

**Estimated Total:** ~55 new tests

---

## 10. Implementation Phases

### Phase 12.0: Infrastructure (~15 tests)
1. Add `ENUM` token to lexer
2. Add `EnumDecl`, `EnumVariant` AST nodes
3. Add `EnumType` to type system
4. Parser: `_enum_decl()` method

### Phase 12.1: Semantic Analysis (~20 tests)
1. Enum type registry in analyzer
2. `_analyze_enum_decl()` method
3. Enum access type resolution in `_get_member_access_expr_type()`
4. Type annotation resolution for enum types
5. Comparison rules for enums

### Phase 12.2: Code Generation (~10 tests)
1. Enum import handling (`from enum import Enum`)
2. `_generate_enum_decl()` method
3. Integration with existing member access codegen

### Phase 12.3: Integration (~10 tests)
1. E2E tests with full compile-run cycle
2. Regression testing

---

## 11. Files to Modify

| File                                    | Changes                            |
| --------------------------------------- | ---------------------------------- |
| `src/quasar/lexer/token_type.py`        | Add `ENUM` token                   |
| `src/quasar/lexer/lexer.py`             | Add `"enum"` keyword               |
| `src/quasar/ast/declarations.py`        | Add `EnumDecl`, `EnumVariant`      |
| `src/quasar/ast/types.py`               | Add `EnumType`                     |
| `src/quasar/ast/__init__.py`            | Export new nodes                   |
| `src/quasar/parser/parser.py`           | Add `_enum_decl()` method          |
| `src/quasar/semantic/analyzer.py`       | Enum analysis logic                |
| `src/quasar/codegen/generator.py`       | Enum code generation               |

---

## 12. Examples

### 12.1 Traffic Light State Machine

```quasar
enum TrafficLight {
    Red,
    Yellow,
    Green
}

fn next_light(current: TrafficLight) -> TrafficLight {
    if current == TrafficLight.Red {
        return TrafficLight.Green
    }
    if current == TrafficLight.Green {
        return TrafficLight.Yellow
    }
    return TrafficLight.Red
}

let light: TrafficLight = TrafficLight.Red
print("Start: Red")

light = next_light(light)
print("After 1: Green")

light = next_light(light)
print("After 2: Yellow")

light = next_light(light)
print("After 3: Red")
```

**Generated Python:**

```python
from enum import Enum

class TrafficLight(Enum):
    Red = "Red"
    Yellow = "Yellow"
    Green = "Green"

def next_light(current):
    if (current == TrafficLight.Red):
        return TrafficLight.Green
    if (current == TrafficLight.Green):
        return TrafficLight.Yellow
    return TrafficLight.Red

light = TrafficLight.Red
print("Start: Red")
light = next_light(light)
print("After 1: Green")
light = next_light(light)
print("After 2: Yellow")
light = next_light(light)
print("After 3: Red")
```

### 12.2 Enum in Struct

```quasar
enum Priority {
    Low,
    Medium,
    High,
    Critical
}

struct Task {
    name: str,
    priority: Priority
}

let task: Task = Task { name: "Fix bug", priority: Priority.High }
print("Task: {}, Priority: {}", task.name, task.priority)

if task.priority == Priority.Critical {
    print("URGENT!")
}
```

---

## 13. Risk Analysis

| Risk                              | Impact | Mitigation                            |
| --------------------------------- | ------ | ------------------------------------- |
| Parser ambiguity (enum vs member) | Medium | Defer to semantic analysis            |
| Name collision with structs       | Low    | Unified namespace in analyzer         |
| Python Enum comparison semantics  | Low    | Python Enum uses identity by default  |
| Performance of type lookups       | Low    | Hash-based dictionaries               |

---

## 14. Success Criteria

- [ ] `enum` keyword recognized by lexer
- [ ] `EnumDecl` parses correctly
- [ ] `Color.Red` resolves to `EnumType("Color")`
- [ ] Type checking for enum assignments
- [ ] `==` and `!=` work for same-type enums
- [ ] Other operators (`<`, `+`, etc.) are rejected
- [ ] Code generates valid Python `enum.Enum`
- [ ] ~55 new tests passing
- [ ] All existing 1022 tests still passing

---

## 15. Timeline

| Week | Milestone                            |
| ---- | ------------------------------------ |
| 1    | Phase 12.0: Infrastructure complete  |
| 2    | Phase 12.1: Semantic analysis done   |
| 3    | Phase 12.2 + 12.3: Codegen + E2E     |
| 4    | Polish, docs, release v1.9.0         |

---

## 16. Decisions Required

> [!IMPORTANT]
> The following decisions need confirmation before implementation:
>
> 1. **Empty enums:** Disallowed (at least one variant required)?
> 2. **Variant naming:** PascalCase enforced or any identifier allowed?
> 3. **Enum comparison semantics:** Identity-based (like Python Enum) is acceptable?

---

**This document is a proposal. Implementation will not begin until this design is FROZEN.**

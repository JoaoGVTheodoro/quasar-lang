# Phase 8 — User Defined Types (Structs): Design Document

**Status:** ✅ FROZEN
**Version:** 1.0.0
**Date:** 2026-01-15
**Author:** Quasar Team
**Depends On:** Phase 7 (FROZEN, v1.4.0)
**Final Test Count:** 854

---

## 1. Executive Summary

Phase 8 introduces **Structs**, allowing developers to define custom attributes grouped under a single type. This is the first step towards complex data modeling in Quasar.

**Key Features:**
- **Keyword:** `struct`
- **Style:** Rust/Swift-like (Nominal typing).
- **Compilation:** Maps to Python `@dataclass`.

---

## 2. Design Specification

### 2.1 Struct Declaration

**Syntax:**
```quasar
struct User {
    name: str,
    age: int,
    active: bool
}
```

**Code Generation (Python):**
```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    active: bool
```

### 2.2 Instantiation

**Syntax:**
```quasar
let u: User = User { name: "Alice", age: 30, active: true }
```

### 2.3 Member Access

```quasar
let name: str = u.name  # Read
u.age = 31              # Write
```

### 2.4 Mutability (Interior Mutability)

- **`let u`**: Variable reassignable. Fields mutable.
- **`const u`**: Variable NOT reassignable. **Fields CAN be mutated.**

---

## 3. Known Constraints

> [!WARNING]
> **Reserved Keywords as Field Names**
> 
> Field names cannot be reserved keywords (`end`, `for`, `if`, etc.).
> Use synonyms: `finish` instead of `end`.

---

## 4. Implementation Phases

| Phase | Description |
|-------|-------------|
| 8.0 | Declaration (`@dataclass`) |
| 8.1 | Instantiation (`Name { field: val }`) |
| 8.2 | Member Access (`.` read/write) |
| 8.3 | Nested Structs & Integration |

---

## 5. Grammar Changes

```ebnf
structDecl   ::= "struct" IDENTIFIER "{" (fieldDecl ("," fieldDecl)* ","?)? "}"
fieldDecl    ::= IDENTIFIER ":" type
structInit   ::= IDENTIFIER "{" (fieldInit ("," fieldInit)* ","?)? "}"
fieldInit    ::= IDENTIFIER ":" expression
```

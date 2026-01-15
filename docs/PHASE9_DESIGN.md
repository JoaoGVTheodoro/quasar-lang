# Phase 9 — Modules & Imports: Design Document

**Status:** ✅ FROZEN
**Version:** 1.0.0
**Date:** 2026-01-15
**Author:** Quasar Team
**Depends On:** Phase 8 (FROZEN, v1.5.0)
**Final Test Count:** 885

---

## 1. Executive Summary

Phase 9 introduces **Modules**, enabling Quasar programs to be split across multiple files and leverage Python's standard library. This is essential for code organization and reuse.

**Key Features:**
- **Python Imports:** Access Python stdlib (e.g., `import math`)
- **Local Imports:** Import other `.qsr` files
- **Qualified Access:** All imports use namespaced access (`math.sqrt`)

---

## 2. Design Specification

### 2.1 Import Syntax

#### Python Standard Library
```quasar
import math
import random

let x: float = math.sqrt(16.0)
let n: int = random.randint(1, 100)
```

#### Local Quasar Files
```quasar
import "./utils.qsr"
import "./models/player.qsr"

let result: int = utils.helper(10)
```

**Syntax Rules:**
- Python modules: bare identifier (`import math`)
- Local files: string literal path (`import "./file.qsr"`)
- No `from X import Y` in v1 (keep simple)
- No aliases (`as`) in v1

### 2.2 Namespace Semantics

When you import a module, its symbols are **not** exposed directly:

```quasar
import math

// ❌ Error: sqrt is not defined
let x: float = sqrt(4.0)

// ✅ Correct: qualified access
let x: float = math.sqrt(4.0)
```

**Symbol Table Changes:**
- Add `ModuleSymbol` to the symbol table
- Modules have their own sub-scope
- Lookups resolve `module.name` in two steps

### 2.3 Code Generation

**Strategy:** Direct mapping to Python imports.

| Quasar | Python |
|--------|--------|
| `import math` | `import math` |
| `import "./utils.qsr"` | `import utils` |
| `import "./models/player.qsr"` | `from models import player` |

**Assumptions:**
- All files in same directory (flat structure for v1)
- Python execution from project root

### 2.4 Circular Dependencies

**Decision:** Defer to Python runtime.

If `a.qsr` imports `b.qsr` and `b.qsr` imports `a.qsr`, the generated Python will have the same circular import. Python may raise `ImportError` at runtime.

**Future:** Semantic analyzer could detect cycles and emit a warning (E09XX).

---

## 3. Implementation Phases

### Phase 9.0: Python Stdlib Imports
- **Goal:** Import Python modules
- **Lexer:** Add `IMPORT` keyword
- **Parser:** Parse `import IDENTIFIER` statement
- **Semantic:** Register module symbol (opaque — no validation of Python contents)
- **CodeGen:** Emit `import X`
- **Tests:** ~15 tests

### Phase 9.1: Local File Imports
- **Goal:** Import `.qsr` files
- **Parser:** Parse `import STRING` statement
- **Semantic:** Compile imported file, register its exports
- **CodeGen:** Strip `.qsr`, emit Python import
- **Tests:** ~20 tests

---

## 4. Grammar Changes

```ebnf
declaration  ::= importDecl | varDecl | constDecl | fnDecl | structDecl | statement

importDecl   ::= "import" ( IDENTIFIER | STRING )
```

---

## 5. AST Nodes

```python
@dataclass
class ImportDecl(Declaration):
    """Import declaration."""
    module: str          # "math" or "./utils.qsr"
    is_local: bool       # True if string path
    span: Span
```

---

## 6. Semantic Analysis

### Phase 9.0 (Python modules)
- Register `ModuleSymbol` with name
- No validation of module contents (trust Python)
- Member access on modules bypasses normal field checking

### Phase 9.1 (Local files)
- Parse and analyze imported file
- Register its top-level exports (functions, structs)
- Validate member access against known exports

---

## 7. Error Codes

| Code | Description |
|------|-------------|
| E0900 | Duplicate import |
| E0901 | Module not found (local files only) |
| E0902 | Circular import detected (optional) |
| E0903 | Unknown symbol in module |

---

## 8. Examples

### Using Python Math
```quasar
import math

fn hypotenuse(a: float, b: float) -> float {
    return math.sqrt(a * a + b * b)
}

print(hypotenuse(3.0, 4.0))  // 5.0
```

### Using Local Module
```quasar
// player.qsr
struct Player { name: str, hp: int }

fn create_player(name: str) -> Player {
    return Player { name: name, hp: 100 }
}
```

```quasar
// main.qsr
import "./player.qsr"

let hero: player.Player = player.create_player("Alice")
print(hero.name)
```

---

## 9. Risk Analysis

| Risk | Mitigation |
|------|------------|
| Python module doesn't exist | Runtime ImportError (acceptable) |
| Conflicting names | Namespacing prevents collisions |
| Complex paths | v1 assumes flat structure |
| Circular imports | Defer to Python runtime |

---

## 10. Open Questions

1. **Type inference for Python modules:** `math.sqrt` returns `float`, but how does Quasar know? 
   - **Proposal:** Treat as `any` (opaque) in v1, add stdlib type stubs later.

2. **Visibility modifiers:** Should Quasar support `pub`/`private`?
   - **Proposal:** All top-level symbols are public by default in v1.

3. **Re-exports:** Can `a.qsr` re-export symbols from `b.qsr`?
   - **Proposal:** Not in v1.

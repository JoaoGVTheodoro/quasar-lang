# Phase 10 — Dictionaries (HashMaps): Design Document

**Status:** ✅ FROZEN
**Version:** 1.0.0
**Date:** 2026-01-15
**Author:** Quasar Team
**Depends On:** Phase 9 (FROZEN, v1.6.0)

---

## 1. Executive Summary

Phase 10 introduces **Dictionaries**, the final core data structure. Dictionaries provide key-value mapping with O(1) average access time.

**Key Features:**
- **Type Syntax:** `Dict[K, V]`
- **Literal Syntax:** `{ key: value }`
- **Operations:** Index read/write (`d[k]`, `d[k] = v`)
- **Compilation:** Direct mapping to Python `dict`

---

## 2. Design Specification

### 2.1 Type Syntax

**Declaration:**
```quasar
let scores: Dict[str, int] = { "Alice": 100, "Bob": 90 }
let lookup: Dict[int, str] = { 1: "one", 2: "two" }
let flags: Dict[str, bool] = { "debug": true }
```

**Key Type Restrictions (v1):**
| Allowed Key Types | Reason             |
| ----------------- | ------------------ |
| `int`             | Hashable primitive |
| `str`             | Hashable primitive |
| `bool`            | Hashable primitive |

> [!WARNING]
> **Not Allowed:** `float`, `[T]`, `Dict[K,V]`, or Structs as keys (not hashable).

### 2.2 Literal Syntax

**Empty Dict:**
```quasar
let empty: Dict[str, int] = {}
```

**With Values:**
```quasar
let ages: Dict[str, int] = {
    "Alice": 30,
    "Bob": 25,
    "Charlie": 35
}
```

**Parser Disambiguation:**
- `{}` in expression context → Empty Dict literal
- `{}` after control flow keyword → Block statement
- `{ EXPR : EXPR }` → Dict literal (colon distinguishes from struct init `{ IDENT : EXPR }`)

### 2.3 Access Operations

**Read (Index):**
```quasar
let score: int = scores["Alice"]  // 100
```

**Write (Index Assignment):**
```quasar
scores["Alice"] = 105
scores["Eve"] = 80  // Creates new key
```

**Runtime Behavior:**
- Read of missing key → **KeyError** (Python default)
- Write to missing key → Creates entry (Python default)

### 2.4 Code Generation

| Quasar               | Python                       |
| -------------------- | ---------------------------- |
| `Dict[str, int]`     | `dict` (or `dict[str, int]`) |
| `{ "a": 1, "b": 2 }` | `{"a": 1, "b": 2}`           |
| `d["key"]`           | `d["key"]`                   |
| `d["key"] = val`     | `d["key"] = val`             |

---

## 3. Type System Integration

### 3.1 DictType Class

Add to `src/quasar/ast/types.py`:

```python
@dataclass(frozen=True)
class DictType:
    """Dict[K, V] type."""
    key_type: QuasarType
    value_type: QuasarType
    
    def __str__(self) -> str:
        return f"Dict[{self.key_type}, {self.value_type}]"
```

Update `QuasarType` union:
```python
QuasarType = Union[PrimitiveType, ListType, DictType]
```

### 3.2 Semantic Rules

**Literal Validation:**
- All keys must be same type
- All values must be same type
- Key type must be hashable (`int`, `str`, `bool`)

**Index Validation:**
- Index key must match declared key type
- Result type is the value type

---

## 4. Implementation Phases

### Phase 10.0: Type & Literal Parsing
- **Lexer:** No new tokens (reuses `{`, `}`, `:`, `,`)
- **AST:** Add `DictType`, `DictLiteral`, `DictEntry`
- **Parser:** Parse `Dict[K, V]` type annotation, `{ k: v }` literals
- **Semantic:** Validate key/value type homogeneity, key hashability
- **CodeGen:** Emit `{k: v}` Python dict literal
- **Tests:** ~20 tests

### Phase 10.1: Index Operations
- **Parser:** Reuse `IndexExpr` for dict access (already handles `expr[expr]`)
- **Semantic:** Detect dict indexing vs list indexing, type check
- **CodeGen:** Same as list index (works for dict in Python)
- **Tests:** ~15 tests

### Phase 10.2: Built-in Methods (Optional)
- `len(d)` → Number of entries (already works via existing `len`)
- `keys(d)` → Returns iterable of keys (new builtin)
- `values(d)` → Returns iterable of values (new builtin)
- **Tests:** ~10 tests

---

## 5. Grammar Changes

```ebnf
type        ::= primitiveType | listType | dictType | IDENTIFIER
dictType    ::= "Dict" "[" type "," type "]"

primary     ::= ... | dictLiteral
dictLiteral ::= "{" (dictEntry ("," dictEntry)* ","?)? "}"
dictEntry   ::= expression ":" expression
```

---

## 6. AST Nodes

```python
@dataclass
class DictEntry(Node):
    """Single key-value pair in dict literal."""
    key: Expression
    value: Expression
    span: Span

@dataclass
class DictLiteral(Expression):
    """Dict literal: { k: v, ... }"""
    entries: list[DictEntry]
    span: Span
```

---

## 7. Error Codes

| Code  | Description                               |
| ----- | ----------------------------------------- |
| E1000 | Heterogeneous key types in dict literal   |
| E1001 | Heterogeneous value types in dict literal |
| E1002 | Non-hashable key type                     |
| E1003 | Index type mismatch (key type)            |
| E1004 | Assignment type mismatch (value type)     |

---

## 8. Examples

### Basic Usage
```quasar
let inventory: Dict[str, int] = {
    "sword": 1,
    "potion": 5,
    "gold": 100
}

print("Potions: {}", inventory["potion"])
inventory["potion"] = inventory["potion"] - 1
```

### With Structs as Values
```quasar
struct Player { name: str, score: int }

let players: Dict[str, Player] = {
    "p1": Player { name: "Alice", score: 100 },
    "p2": Player { name: "Bob", score: 80 }
}

let alice: Player = players["p1"]
print("Score: {}", alice.score)
```

### Iteration (Future)
```quasar
// Phase 10.3 (future)
for key in keys(inventory) {
    print("{}: {}", key, inventory[key])
}
```

---

## 9. Risk Analysis

| Risk                             | Mitigation                                |
| -------------------------------- | ----------------------------------------- |
| Parser ambiguity (`{}` vs block) | Context-aware parsing                     |
| Empty dict type inference        | Require explicit type annotation          |
| KeyError at runtime              | Document behavior, future `.get()` method |

---

## 9.1 Known Constraints

> **Note:** Checking for key existence requires iterating over `keys(d)` until `haskey()` or `in` operator is implemented. See `examples/frequency.qsr` for workaround pattern.

---

## 10. Open Questions

1. **Empty Dict Inference:** Should `let d = {}` be allowed without type annotation?
   - **Proposal:** No, require `let d: Dict[str, int] = {}` for clarity.

2. **Nested Dicts:** `Dict[str, Dict[str, int]]`?
   - **Proposal:** Yes, supported naturally via recursive type.

3. **Dict in Struct:** Can struct have dict field?
   - **Proposal:** Yes, `struct Config { settings: Dict[str, str] }`

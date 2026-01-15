# Phase 6 — Data Structures & Control Flow: Design Document

**Status:** ✅ FROZEN  
**Version:** 1.3.0  
**Date:** 2026-01-15  
**Author:** Quasar Team  
**Depends On:** Phase 5.2 (FROZEN)

---

## Final Test Results

| Sub-Phase | Description             | Tests Added | Total   |
| --------- | ----------------------- | ----------- | ------- |
| 6.0       | Type System Foundation  | +46         | 583     |
| 6.1       | Index Access & Mutation | +34         | 617     |
| 6.2       | Built-in Functions      | +30         | 647     |
| 6.3       | For Loops & Ranges      | +39         | 686     |
| 6.4       | Integration Tests       | +33         | **719** |

**All 719 tests passing.** Phase 6 is now frozen.

---

## 1. Executive Summary

Phase 6 introduces **composite data types** (Lists) and **iterator-based control flow** (for loops with ranges). This is the largest structural change since Phase 0, requiring modifications to the Type System, Lexer, Parser, Semantic Analyzer, and Code Generator.

### Scope Definition

| In Scope                         | Out of Scope                  |
| -------------------------------- | ----------------------------- |
| List type declaration `[T]`      | Dictionaries/Maps `{K: V}`    |
| List literals `[1, 2, 3]`        | Tuples `(a, b, c)`            |
| Index access `list[i]`           | Slicing `list[1:3]`           |
| Index assignment `list[i] = val` | List comprehensions           |
| Built-in `len(list)`             | `map`, `filter`, `reduce`     |
| Built-in `push(list, val)`       | `pop`, `insert`, `remove`     |
| `for item in list { }`           | `for` with multiple iterators |
| Range expressions `start..end`   | Step ranges `0..10..2`        |
| Homogeneous type enforcement     | Union types `[int \| str]`    |

### Backward Compatibility

✅ **100% backward compatible** — All existing Quasar programs remain valid.

---

## 2. Design Decisions

### 2.1 List Type Syntax

**Decision:** Use bracket notation `[T]` for list types.

**Syntax:**
```quasar
let numbers: [int] = [1, 2, 3]
let names: [str] = ["Alice", "Bob"]
let matrix: [[int]] = [[1, 2], [3, 4]]
let empty: [float] = []
```

**Rationale:**
| Option    | Example     | Pros                                | Cons                           |
| --------- | ----------- | ----------------------------------- | ------------------------------ |
| `[T]`     | `[int]`     | Clean, Rust/Swift-like, no keywords | May confuse with array literal |
| `List<T>` | `List<int>` | Explicit, Java/C#-like              | Verbose, requires `<>` parsing |
| `list[T]` | `list[int]` | Python-like                         | Inconsistent (lowercase type)  |

**Choice: `[T]`** — Aligns with Quasar's "clean and explicit" philosophy. The context (type annotation vs expression) disambiguates usage.

### 2.2 List Literal Syntax

**Decision:** Square brackets with comma-separated elements.

**Syntax:**
```quasar
[1, 2, 3]           // [int]
["a", "b", "c"]     // [str]
[true, false]       // [bool]
[[1, 2], [3, 4]]    // [[int]]
[]                  // Empty list (requires type annotation)
```

**Rules:**
1. All elements must have the same type (homogeneous)
2. Empty list `[]` requires explicit type annotation
3. Trailing comma allowed: `[1, 2, 3,]`

### 2.3 Index Access

**Decision:** Zero-based indexing with bracket notation.

**Syntax:**
```quasar
let nums: [int] = [10, 20, 30]
let first: int = nums[0]      // 10
let last: int = nums[2]       // 30
let nested: [[int]] = [[1, 2], [3, 4]]
let val: int = nested[0][1]   // 2
```

**Runtime Behavior:**
- Out-of-bounds access raises Python `IndexError` (no compile-time check)
- Negative indices NOT supported (explicit design choice for simplicity)

### 2.4 Mutability Rules (CRITICAL)

**Decision:** `const` applies to the binding, NOT the container contents.

**Rules:**

| Declaration                  | Rebind Variable | Modify Element  | Resize List       |
| ---------------------------- | --------------- | --------------- | ----------------- |
| `let list: [int] = [1, 2]`   | ✅ `list = [3]`  | ✅ `list[0] = 9` | ✅ `push(list, 3)` |
| `const list: [int] = [1, 2]` | ❌ Error E0003   | ✅ `list[0] = 9` | ✅ `push(list, 3)` |

**Rationale:**
- Follows Rust/JavaScript semantics for `const` (binding immutability)
- `const` prevents reassignment, not mutation
- Full immutability (frozen lists) is OUT OF SCOPE for Phase 6

**Example:**
```quasar
const numbers: [int] = [1, 2, 3]
numbers[0] = 10      // ✅ OK - modifying element
push(numbers, 4)     // ✅ OK - adding element
numbers = [5, 6]     // ❌ E0003: cannot reassign const
```

### 2.5 For Loop Syntax

**Decision:** Iterator-based `for-in` loop with mandatory braces.

**Syntax:**
```quasar
for item in collection {
    // body
}
```

**Examples:**
```quasar
// Iterate over list
let names: [str] = ["Alice", "Bob", "Carol"]
for name in names {
    print("Hello, {}!", name)
}

// Iterate over range
for i in 0..5 {
    print("Index: {}", i)
}

// Nested loops
for row in matrix {
    for col in row {
        print("{}", col)
    }
}
```

**Loop Variable Scoping:**
- Loop variable is scoped to the loop body
- Loop variable is immutable within the body (cannot reassign `item`)
- Loop variable shadows outer variables with same name

### 2.6 Range Expressions

**Decision:** Exclusive end range with `..` operator.

**Syntax:**
```quasar
start..end    // Exclusive: [start, end)
```

**Examples:**
```quasar
0..5          // 0, 1, 2, 3, 4
1..4          // 1, 2, 3
10..10        // Empty range
```

**Rules:**
1. `start` and `end` must be `int` type
2. Range is exclusive (end not included) — matches Rust/Python
3. `start > end` produces empty range (no error)
4. Ranges are NOT first-class values (only valid in `for` context)

**Out of Scope:**
- Inclusive ranges `0..=5` — Future consideration
- Step ranges `0..10..2` — Future consideration
- Range as standalone expression — Future consideration

### 2.7 Built-in Functions

**Decision:** Add `len()` and `push()` as built-in functions.

#### `len(list) -> int`

Returns the number of elements in a list.

```quasar
let nums: [int] = [1, 2, 3]
print("Length: {}", len(nums))  // Length: 3
```

#### `push(list, value) -> void`

Appends an element to the end of a list. Modifies in-place.

```quasar
let nums: [int] = [1, 2]
push(nums, 3)
print("{}", nums)  // [1, 2, 3]
```

**Type Constraints:**
- `push(list: [T], value: T)` — value must match list element type

---

## 3. Type System Changes

### 3.1 Current Type System

```python
class TypeAnnotation(Enum):
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STR = "str"
    VOID = "void"
```

**Problem:** Cannot represent composite types like `[int]` or `[[str]]`.

### 3.2 Proposed Type System

**Decision:** Replace Enum with a class hierarchy.

```python
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class PrimitiveType:
    """Primitive types: int, float, bool, str, void"""
    name: str  # "int", "float", "bool", "str", "void"

@dataclass(frozen=True)
class ListType:
    """List type: [T] where T is element type"""
    element_type: "QuasarType"

# Type alias for all types
QuasarType = Union[PrimitiveType, ListType]

# Convenience constructors
INT = PrimitiveType("int")
FLOAT = PrimitiveType("float")
BOOL = PrimitiveType("bool")
STR = PrimitiveType("str")
VOID = PrimitiveType("void")

def list_of(element_type: QuasarType) -> ListType:
    return ListType(element_type)

# Examples:
# [int]      -> ListType(INT)
# [[str]]    -> ListType(ListType(STR))
# [[[bool]]] -> ListType(ListType(ListType(BOOL)))
```

### 3.3 Migration Strategy

1. Create new `types.py` module with class-based types
2. Update `TypeAnnotation` references throughout codebase
3. Maintain backward compatibility for primitive type comparisons
4. Add type equality and string representation methods

---

## 4. AST Changes

### 4.1 New AST Nodes

```python
@dataclass
class ListLiteral(Expression):
    """List literal: [expr, expr, ...]"""
    elements: list[Expression]
    span: Span

@dataclass
class IndexExpr(Expression):
    """Index access: expr[index]"""
    target: Expression
    index: Expression
    span: Span

@dataclass  
class IndexAssignStmt(Statement):
    """Index assignment: expr[index] = value"""
    target: Expression
    index: Expression
    value: Expression
    span: Span

@dataclass
class RangeExpr(Expression):
    """Range expression: start..end"""
    start: Expression
    end: Expression
    span: Span

@dataclass
class ForStmt(Statement):
    """For loop: for var in iterable { body }"""
    variable: str
    iterable: Expression  # ListLiteral, Identifier, or RangeExpr
    body: Block
    span: Span
```

### 4.2 Type Annotation AST

```python
@dataclass
class TypeNode:
    """Base class for type annotations in AST"""
    span: Span

@dataclass
class PrimitiveTypeNode(TypeNode):
    """Primitive type: int, float, bool, str"""
    name: str

@dataclass
class ListTypeNode(TypeNode):
    """List type: [T]"""
    element_type: TypeNode
```

---

## 5. Lexer Changes

### 5.1 New Tokens

| Token      | Pattern | Description    |
| ---------- | ------- | -------------- |
| `LBRACKET` | `[`     | Left bracket   |
| `RBRACKET` | `]`     | Right bracket  |
| `DOTDOT`   | `..`    | Range operator |
| `FOR`      | `for`   | For keyword    |
| `IN`       | `in`    | In keyword     |

### 5.2 Token Disambiguation

The `[` token has multiple contexts:
1. **Type annotation:** `let x: [int]`
2. **List literal:** `let x = [1, 2, 3]`
3. **Index access:** `x[0]`

**Resolution:** Parser handles disambiguation based on context.

---

## 6. Parser Changes

### 6.1 Grammar Extensions

```ebnf
(* Type annotations *)
type_annotation = primitive_type | list_type ;
primitive_type  = "int" | "float" | "bool" | "str" ;
list_type       = "[" type_annotation "]" ;

(* Expressions *)
primary         = literal | identifier | "(" expression ")" | list_literal ;
list_literal    = "[" [ expression { "," expression } [ "," ] ] "]" ;
postfix         = primary { index_access | call } ;
index_access    = "[" expression "]" ;

(* Range - only in for context *)
range_expr      = expression ".." expression ;

(* Statements *)
for_stmt        = "for" IDENTIFIER "in" ( range_expr | expression ) block ;
index_assign    = postfix "=" expression ;
```

### 6.2 Precedence Changes

| Level       | Operators               | Associativity   |
| ----------- | ----------------------- | --------------- |
| 1 (highest) | `()` `[]` (call, index) | Left            |
| 2           | `!` `-` (unary)         | Right           |
| 3           | `*` `/` `%`             | Left            |
| 4           | `+` `-`                 | Left            |
| 5           | `..` (range)            | Non-associative |
| 6           | `<` `>` `<=` `>=`       | Left            |
| 7           | `==` `!=`               | Left            |
| 8           | `and`                   | Left            |
| 9           | `or`                    | Left            |

---

## 7. Semantic Analysis Changes

### 7.1 New Error Codes

| Code  | Description                       | Example                    |
| ----- | --------------------------------- | -------------------------- |
| E0500 | Heterogeneous list literal        | `[1, "a", true]`           |
| E0501 | Index type must be int            | `list["0"]`                |
| E0502 | Cannot index non-list type        | `42[0]`                    |
| E0503 | Type mismatch in index assignment | `let x: [int]; x[0] = "a"` |
| E0504 | Range bounds must be int          | `"a".."z"`                 |
| E0505 | Cannot iterate over non-iterable  | `for x in 42 { }`          |
| E0506 | push() argument type mismatch     | `push([1, 2], "a")`        |
| E0507 | len() requires list argument      | `len(42)`                  |

### 7.2 Type Inference for Lists

```quasar
// Type inferred from elements
let nums = [1, 2, 3]           // [int]
let strs = ["a", "b"]          // [str]

// Empty list requires annotation
let empty: [int] = []          // OK
let bad = []                   // E????: cannot infer type of empty list
```

### 7.3 For Loop Type Checking

```quasar
let nums: [int] = [1, 2, 3]
for n in nums {
    // n has type int (inferred from list element type)
    let doubled: int = n * 2   // OK
    let bad: str = n           // E0100: type mismatch
}

for i in 0..10 {
    // i has type int (ranges always produce int)
}
```

---

## 8. Code Generation

### 8.1 List Operations

| Quasar                     | Python          |
| -------------------------- | --------------- |
| `let x: [int] = [1, 2, 3]` | `x = [1, 2, 3]` |
| `x[0]`                     | `x[0]`          |
| `x[0] = 10`                | `x[0] = 10`     |
| `len(x)`                   | `len(x)`        |
| `push(x, 4)`               | `x.append(4)`   |

### 8.2 For Loop Generation

| Quasar                   | Python                            |
| ------------------------ | --------------------------------- |
| `for x in list { body }` | `for x in list:\n    body`        |
| `for i in 0..5 { body }` | `for i in range(0, 5):\n    body` |

### 8.3 Nested Examples

```quasar
// Quasar
let matrix: [[int]] = [[1, 2], [3, 4]]
for row in matrix {
    for col in row {
        print("{}", col)
    }
}
```

```python
# Generated Python
matrix = [[1, 2], [3, 4]]
for row in matrix:
    for col in row:
        print("{}".format(col))
```

---

## 9. Implementation Strategy

### Phase 6.0 — List Types & Literals (Foundation)

**Scope:**
- New type system (`QuasarType` classes)
- Lexer: `LBRACKET`, `RBRACKET` tokens
- Parser: List type annotations, list literals
- Semantic: Homogeneous type validation (E0500)
- CodeGen: List literal generation

**Deliverables:**
```quasar
let nums: [int] = [1, 2, 3]
let strs: [str] = ["a", "b"]
let nested: [[int]] = [[1], [2]]
let empty: [int] = []
```

**Test Target:** +30 tests

---

### Phase 6.1 — Index Access & Mutation

**Scope:**
- AST: `IndexExpr`, `IndexAssignStmt`
- Parser: Index access parsing
- Semantic: Index type validation (E0501, E0502, E0503)
- CodeGen: Index access/assignment generation

**Deliverables:**
```quasar
let nums: [int] = [1, 2, 3]
let first: int = nums[0]
nums[1] = 10
let val: int = matrix[0][1]
```

**Test Target:** +25 tests

---

### Phase 6.2 — Built-in Functions (len, push)

**Scope:**
- Semantic: Built-in function type checking (E0506, E0507)
- CodeGen: `len()` → `len()`, `push()` → `.append()`

**Deliverables:**
```quasar
let nums: [int] = [1, 2]
print("Length: {}", len(nums))
push(nums, 3)
```

**Test Target:** +20 tests

---

### Phase 6.3 — Ranges & For Loops

**Scope:**
- Lexer: `DOTDOT`, `FOR`, `IN` tokens
- AST: `RangeExpr`, `ForStmt`
- Parser: Range and for loop parsing
- Semantic: Iterator type inference (E0504, E0505)
- CodeGen: For loop generation

**Deliverables:**
```quasar
for i in 0..10 {
    print("{}", i)
}

for item in list {
    print("{}", item)
}
```

**Test Target:** +35 tests

---

### Phase 6.4 — Integration & Polish

**Scope:**
- E2E integration tests
- Edge cases and error messages
- Documentation updates

**Test Target:** +20 tests

---

## 10. Test Budget Summary

| Sub-Phase | Component Changes     | New Tests | Cumulative |
| --------- | --------------------- | --------- | ---------- |
| 6.0       | Type System, Literals | +30       | 567        |
| 6.1       | Index Access          | +25       | 592        |
| 6.2       | len, push             | +20       | 612        |
| 6.3       | Ranges, For           | +35       | 647        |
| 6.4       | Integration           | +20       | 667        |
| **Total** | —                     | **+130**  | **667**    |

---

## 11. Risk Assessment

### High Risk Areas

| Area                    | Risk                       | Mitigation                           |
| ----------------------- | -------------------------- | ------------------------------------ |
| Type System Refactor    | Breaking existing code     | Comprehensive regression tests       |
| Parser Complexity       | Ambiguous `[` token        | Clear context-based disambiguation   |
| Semantic Type Inference | Edge cases in nested types | Explicit type annotation requirement |

### Breaking Change Analysis

**None expected.** All changes are additive:
- New tokens don't conflict with existing syntax
- New AST nodes extend existing hierarchy
- Type system refactor maintains backward compatibility for primitives

---

## 12. Open Questions

### Q1: Should empty list inference be supported?

```quasar
let x = []  // What type?
```

**Options:**
- A) Require explicit annotation: `let x: [int] = []`
- B) Infer from first assignment: `x = [1]` makes `x: [int]`
- C) Error: cannot infer type

**Recommendation:** Option A (explicit annotation required)

### Q2: Should `for` support `break` and `continue`?

```quasar
for i in 0..10 {
    if i == 5 {
        break  // Exit loop?
    }
}
```

**Options:**
- A) Support both (consistent with `while`)
- B) Defer to future phase
- C) Not supported (functional style)

**Recommendation:** Option A (already implemented for `while`)

### Q3: Should list comparison be supported?

```quasar
let a: [int] = [1, 2, 3]
let b: [int] = [1, 2, 3]
if a == b { ... }  // Structural equality?
```

**Options:**
- A) Support structural equality
- B) Reference equality only
- C) Not supported (explicit `equals()` function)

**Recommendation:** Defer to future phase

---

## 13. Future Considerations (Out of Scope)

- **Slicing:** `list[1:3]`
- **Negative indexing:** `list[-1]`
- **List methods:** `.pop()`, `.insert()`, `.remove()`, `.reverse()`
- **List comprehensions:** `[x * 2 for x in list]`
- **Iterators:** `iter()`, `next()`
- **Tuples:** `(a, b, c)`
- **Dictionaries:** `{key: value}`
- **Sets:** `{1, 2, 3}`
- **Immutable lists:** `const!` or `freeze()`

---

## 14. Approval Checklist

- [ ] Type syntax `[T]` approved
- [ ] Mutability rules (const = binding only) approved
- [ ] For loop syntax approved
- [ ] Range syntax `start..end` (exclusive) approved
- [ ] Sub-phase division (6.0-6.4) approved
- [ ] Test budget (+130) approved
- [ ] Open questions resolved

---

**Document Status:** AWAITING REVIEW

**Next Step:** Address open questions, then begin Phase 6.0 implementation.

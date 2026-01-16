# Phase 11 — Standard Library (Primitive Methods): Design Document

**Status:** FROZEN ✅
**Version:** 1.0.0
**Date:** 2026-01-16
**Author:** Quasar Team
**Depends On:** Phase 10 (FROZEN, v1.7.0)

---

## Progress Tracker

| Sub-Phase | Description                            | Status | Tests |
| --------- | -------------------------------------- | ------ | ----- |
| 11.0      | Infrastructure (AST, Parser, Registry) | ✅ DONE | 18    |
| 11.1      | String Methods                         | ✅ DONE | 31    |
| 11.2      | Collection Methods (List + Dict)       | ✅ DONE | 32    |

**Total Phase 11 Tests:** 81
**Total Project Tests:** 1022

---

## 1. Executive Summary

Phase 11 introduces **Primitive Methods** — method syntax for built-in types (`str`, `[T]`, `Dict[K,V]`). This improves usability and brings Quasar closer to modern language ergonomics.

**Key Features:**
- **Method Syntax:** `value.method()` for primitives
- **String Methods:** `upper()`, `lower()`, `split()`, `trim()`, etc.
- **List Methods:** `push()`, `pop()`, `contains()`, `join()`
- **Dict Methods:** `has_key()`, `get()`, `remove()`, `clear()`

**Motivation:**
- v1.7.0 limitation: Checking dict key existence requires manual iteration
- Functional style (`len(s)`) vs OOP style (`s.len()`) — support both
- Python interop: Direct mapping to Python methods

---

## 2. Architecture: Virtual Method Table for Primitives

### 2.1 Current Limitation

Currently, `obj.member` only works for Struct types:

```python
# Current SemanticAnalyzer._get_member_access_expr_type()
def _get_member_access_expr_type(self, expr: MemberAccessExpr) -> QuasarType:
    obj_type = self._get_expression_type(expr.object)
    # Only checks struct fields...
```

### 2.2 Proposed Solution

Introduce a **Primitive Method Registry** that maps:
- Type → Method Name → (Parameter Types, Return Type)

```python
# Conceptual structure
PRIMITIVE_METHODS: dict[str, dict[str, MethodSignature]] = {
    "str": {
        "upper": MethodSignature(params=[], returns=STR),
        "split": MethodSignature(params=[STR], returns=ListType(STR)),
        # ...
    },
    "list": {
        "push": MethodSignature(params=["T"], returns=VOID),
        "pop": MethodSignature(params=[], returns="T"),
        # ...
    },
    "dict": {
        "has_key": MethodSignature(params=["K"], returns=BOOL),
        "get": MethodSignature(params=["K", "V"], returns="V"),
        # ...
    },
}
```

### 2.3 Resolution Flow

When analyzing `expr.method(args)`:

```
1. Get type of `expr` → T
2. If T is Struct:
   → Existing logic (field access or future struct methods)
3. If T is Primitive (str, int, float, bool):
   → Lookup in PRIMITIVE_METHODS["str"]
4. If T is ListType:
   → Lookup in PRIMITIVE_METHODS["list"], substitute element type
5. If T is DictType:
   → Lookup in PRIMITIVE_METHODS["dict"], substitute K/V types
6. Validate argument types against signature
7. Return declared return type
```

---

## 3. String Methods Specification

### 3.1 Method Table

| Quasar Method           | Signature           | Python Equivalent      | Description                |
| ----------------------- | ------------------- | ---------------------- | -------------------------- |
| `s.len()`               | `() -> int`         | `len(s)`               | String length              |
| `s.upper()`             | `() -> str`         | `s.upper()`            | Uppercase copy             |
| `s.lower()`             | `() -> str`         | `s.lower()`            | Lowercase copy             |
| `s.trim()`              | `() -> str`         | `s.strip()`            | Remove whitespace          |
| `s.trim_start()`        | `() -> str`         | `s.lstrip()`           | Remove leading whitespace  |
| `s.trim_end()`          | `() -> str`         | `s.rstrip()`           | Remove trailing whitespace |
| `s.split(sep)`          | `(str) -> [str]`    | `s.split(sep)`         | Split into list            |
| `s.replace(old, new)`   | `(str, str) -> str` | `s.replace(old, new)`  | Replace occurrences        |
| `s.contains(sub)`       | `(str) -> bool`     | `sub in s`             | Check substring            |
| `s.starts_with(prefix)` | `(str) -> bool`     | `s.startswith(prefix)` | Check prefix               |
| `s.ends_with(suffix)`   | `(str) -> bool`     | `s.endswith(suffix)`   | Check suffix               |
| `s.to_int()`            | `() -> int`         | `int(s)`               | Parse as integer           |
| `s.to_float()`          | `() -> float`       | `float(s)`             | Parse as float             |

### 3.2 Examples

```quasar
let name: str = "  Alice  "
let trimmed: str = name.trim()        # "Alice"
let upper: str = trimmed.upper()      # "ALICE"

let csv: str = "a,b,c"
let parts: [str] = csv.split(",")     # ["a", "b", "c"]

let text: str = "hello world"
let replaced: str = text.replace("world", "quasar")  # "hello quasar"

if text.contains("hello") {
    print("Found!")
}

let num_str: str = "42"
let num: int = num_str.to_int()       # 42
```

### 3.3 Code Generation

| Quasar             | Python            |
| ------------------ | ----------------- |
| `s.len()`          | `len(s)`          |
| `s.upper()`        | `s.upper()`       |
| `s.trim()`         | `s.strip()`       |
| `s.contains(x)`    | `(x in s)`        |
| `s.starts_with(x)` | `s.startswith(x)` |
| `s.to_int()`       | `int(s)`          |

---

## 4. List Methods Specification

### 4.1 Method Table

| Quasar Method   | Signature      | Python Equivalent | Description                   |
| --------------- | -------------- | ----------------- | ----------------------------- |
| `l.len()`       | `() -> int`    | `len(l)`          | List length                   |
| `l.push(v)`     | `(T) -> void`  | `l.append(v)`     | Append element                |
| `l.pop()`       | `() -> T`      | `l.pop()`         | Remove and return last        |
| `l.contains(v)` | `(T) -> bool`  | `v in l`          | Check membership              |
| `l.index_of(v)` | `(T) -> int`   | `l.index(v)`      | Find index (-1 if not found)* |
| `l.join(sep)`   | `(str) -> str` | `sep.join(l)`     | Join with separator           |
| `l.reverse()`   | `() -> void`   | `l.reverse()`     | Reverse in-place              |
| `l.clear()`     | `() -> void`   | `l.clear()`       | Remove all elements           |

> *Note: Python's `list.index()` raises ValueError if not found. We may wrap with try/except or use a different implementation.

### 4.2 Type Parameterization

List methods must respect the element type `T`:

```quasar
let nums: [int] = [1, 2, 3]
nums.push(4)        # OK: 4 is int
nums.push("x")      # ERROR E1100: cannot push str to [int]

let found: bool = nums.contains(2)  # OK
let found: bool = nums.contains("x") # ERROR E1101: contains() expects int
```

### 4.3 Special Case: `join()`

In Python, `join` is a string method: `",".join(list)`.
In Quasar, we want: `list.join(",")`.

**Code Generation:**
```python
# Quasar: parts.join(",")
# Python: ",".join(parts)
```

**Constraint:** `join()` only valid for `[str]` lists.

```quasar
let words: [str] = ["a", "b", "c"]
let csv: str = words.join(",")  # OK: "a,b,c"

let nums: [int] = [1, 2, 3]
let bad: str = nums.join(",")   # ERROR E1102: join() requires [str]
```

### 4.4 Examples

```quasar
let items: [str] = ["apple", "banana"]
items.push("cherry")
print(items.len())              # 3

if items.contains("banana") {
    print("Has banana!")
}

let last: str = items.pop()     # "cherry"
let csv: str = items.join(", ") # "apple, banana"
```

---

## 5. Dictionary Methods Specification

### 5.1 Method Table

| Quasar Method       | Signature     | Python Equivalent   | Description        |
| ------------------- | ------------- | ------------------- | ------------------ |
| `d.len()`           | `() -> int`   | `len(d)`            | Number of entries  |
| `d.has_key(k)`      | `(K) -> bool` | `k in d`            | Check key exists   |
| `d.get(k, default)` | `(K, V) -> V` | `d.get(k, default)` | Get with default   |
| `d.keys()`          | `() -> [K]`   | `list(d.keys())`    | All keys as list   |
| `d.values()`        | `() -> [V]`   | `list(d.values())`  | All values as list |
| `d.remove(k)`       | `(K) -> void` | `d.pop(k, None)`    | Remove entry       |
| `d.clear()`         | `() -> void`  | `d.clear()`         | Remove all entries |

### 5.2 Priority: `has_key()`

This method is **high priority** as it resolves the v1.7.0 limitation:

```quasar
# v1.7.0 workaround (verbose)
fn contains(key: str, dict_keys: [str]) -> bool {
    for k in 0..len(dict_keys) {
        if dict_keys[k] == key {
            return true
        }
    }
    return false
}

let exists: bool = contains("key", keys(d))

# v1.8.0 with has_key() (clean)
let exists: bool = d.has_key("key")
```

### 5.3 Type Parameterization

Dict methods must respect `K` and `V` types:

```quasar
let scores: Dict[str, int] = { "Alice": 100 }

# has_key: argument must be K (str)
scores.has_key("Bob")    # OK
scores.has_key(123)      # ERROR E1103: has_key() expects str key

# get: arguments must be (K, V)
let s: int = scores.get("Bob", 0)      # OK: returns 0 if missing
let s: int = scores.get("Bob", "none") # ERROR E1104: default must be int
```

### 5.4 Examples

```quasar
let inventory: Dict[str, int] = { "sword": 1, "potion": 5 }

if inventory.has_key("shield") {
    print("Has shield!")
} else {
    print("No shield")
}

let potions: int = inventory.get("potion", 0)
let armor: int = inventory.get("armor", 0)  # Returns 0 (default)

inventory.remove("sword")
print(inventory.len())  # 1

inventory.clear()
print(inventory.len())  # 0
```

---

## 6. AST Changes

### 6.1 Method Call Expression

We need to distinguish between:
- Field access: `obj.field` → `MemberAccessExpr`
- Method call: `obj.method()` → `MethodCallExpr` (NEW)

```python
@dataclass
class MethodCallExpr(Expression):
    """Method call on an object: obj.method(args)"""
    object: Expression
    method: str
    arguments: list[Expression]
    span: Span
```

### 6.2 Parser Changes

Currently `_postfix()` handles:
- `expr(args)` → CallExpr
- `expr[index]` → IndexExpr
- `expr.member` → MemberAccessExpr

Add detection for `expr.member(args)` → MethodCallExpr

---

## 7. Semantic Analysis Changes

### 7.1 Primitive Method Registry

```python
@dataclass
class MethodSignature:
    """Signature for a primitive method."""
    params: list[QuasarType]  # Use VOID for "T" placeholder
    returns: QuasarType
    is_generic: bool = False  # True if uses T, K, V

# Registry structure
PRIMITIVE_METHODS = {
    "str": {
        "upper": MethodSignature(params=[], returns=STR),
        "split": MethodSignature(params=[STR], returns=ListType(STR)),
        "contains": MethodSignature(params=[STR], returns=BOOL),
        # ...
    },
    # ...
}
```

### 7.2 New Analyzer Method

```python
def _get_method_call_expr_type(self, expr: MethodCallExpr) -> QuasarType:
    """Analyze method call on primitive or collection type."""
    obj_type = self._get_expression_type(expr.object)
    
    # Determine which method table to use
    if obj_type == STR:
        methods = PRIMITIVE_METHODS["str"]
    elif isinstance(obj_type, ListType):
        methods = PRIMITIVE_METHODS["list"]
    elif isinstance(obj_type, DictType):
        methods = PRIMITIVE_METHODS["dict"]
    else:
        raise SemanticError(...)
    
    # Lookup method
    if expr.method not in methods:
        raise SemanticError(
            code="E1105",
            message=f"type '{obj_type}' has no method '{expr.method}'"
        )
    
    sig = methods[expr.method]
    # Validate arguments...
    # Substitute generic types (T, K, V)...
    return sig.returns
```

---

## 8. Code Generation Changes

### 8.1 Method Call Generator

```python
def _generate_method_call_expr(self, expr: MethodCallExpr) -> str:
    obj = self._generate_expression(expr.object)
    args = ", ".join(self._generate_expression(a) for a in expr.arguments)
    
    # Special cases
    if expr.method == "trim":
        return f"{obj}.strip()"
    if expr.method == "contains" and is_string(expr.object):
        return f"({args} in {obj})"
    if expr.method == "has_key":
        return f"({args} in {obj})"
    if expr.method == "join":
        return f"{args}.join({obj})"
    if expr.method == "len":
        return f"len({obj})"
    if expr.method == "to_int":
        return f"int({obj})"
    
    # Default: direct mapping
    return f"{obj}.{expr.method}({args})"
```

---

## 9. Error Codes

| Code  | Description                                 |
| ----- | ------------------------------------------- |
| E1100 | List method type mismatch (push wrong type) |
| E1101 | List contains() argument type mismatch      |
| E1102 | List join() requires [str]                  |
| E1103 | Dict has_key() key type mismatch            |
| E1104 | Dict get() default value type mismatch      |
| E1105 | Type has no such method                     |
| E1106 | Method argument count mismatch              |
| E1107 | Method argument type mismatch               |

---

## 10. Implementation Phases

### Phase 11.0: Infrastructure (~30 tests)
- Add `MethodCallExpr` AST node
- Update Parser to recognize `expr.method(args)`
- Add Primitive Method Registry
- Basic semantic validation framework
- Code generation framework

### Phase 11.1: String Methods (~25 tests)
- Implement all string methods
- `upper()`, `lower()`, `trim()`, `split()`, `replace()`
- `contains()`, `starts_with()`, `ends_with()`
- `to_int()`, `to_float()`, `len()`

### Phase 11.2: Collection Methods (~30 tests)
- List methods: `push()`, `pop()`, `contains()`, `join()`, `len()`
- Dict methods: `has_key()`, `get()`, `remove()`, `keys()`, `values()`, `len()`

**Estimated Total:** ~85 new tests

---

## 11. Migration & Compatibility

### 11.1 Backward Compatibility

Existing global functions remain valid:
```quasar
# Both work in v1.8.0
let n: int = len(s)      # Global function (existing)
let n: int = s.len()     # Method syntax (new)

let k: [str] = keys(d)   # Global function (existing)
let k: [str] = d.keys()  # Method syntax (new)
```

### 11.2 Deprecation Strategy

No deprecations in v1.8.0. Global functions and methods coexist.
Future versions may recommend method style but won't remove globals.

---

## 12. Examples

### 12.1 Improved Vote Counter (v1.8.0)

```quasar
# frequency.qsr - Simplified with has_key()

let votes: [str] = ["blue", "red", "blue", "green", "red", "blue"]
let counts: Dict[str, int] = {}

for i in 0..votes.len() {
    let vote: str = votes[i]
    
    if counts.has_key(vote) {
        counts[vote] = counts[vote] + 1
    } else {
        counts[vote] = 1
    }
}

print("Results: blue={}, red={}, green={}", 
    counts.get("blue", 0),
    counts.get("red", 0),
    counts.get("green", 0))
```

### 12.2 String Processing

```quasar
let input: str = "  Hello, World!  "
let clean: str = input.trim().lower()
let words: [str] = clean.split(" ")

for i in 0..words.len() {
    print("Word {}: {}", i, words[i])
}

let csv: str = words.join(",")
print("CSV: {}", csv)
```

---

## 13. Open Questions

1. **Method vs Function Priority:**
   If both `push(list, val)` and `list.push(val)` exist, which is preferred in docs?
   - **Proposal:** Document method style as primary, note function style as alternative.

2. **Chaining:**
   Should `"  hello  ".trim().upper()` work?
   - **Proposal:** Yes, naturally supported if each method returns appropriate type.

3. **Mutable Methods:**
   Methods like `reverse()`, `clear()` mutate in-place. Should we also offer immutable versions?
   - **Proposal:** v1.8 focuses on Python-compatible mutable methods. Immutable variants (e.g., `reversed()`) deferred.

4. **Error Handling:**
   What if `s.to_int()` fails on invalid input?
   - **Proposal:** Runtime error (Python's ValueError). Future: Result type or try/catch.

---

## 14. Risk Analysis

| Risk                               | Impact | Mitigation                           |
| ---------------------------------- | ------ | ------------------------------------ |
| Parser ambiguity: `x.y()` vs `x.y` | Medium | Lookahead for `(` after member       |
| Generic type substitution bugs     | High   | Extensive testing with various types |
| Python method name mismatches      | Low    | Explicit mapping table               |
| Performance (method lookup)        | Low    | Compile-time resolution              |

---

## 15. Success Criteria

- [ ] All 13 string methods implemented and tested
- [ ] All 8 list methods implemented and tested
- [ ] All 7 dict methods implemented and tested
- [ ] `has_key()` resolves v1.7.0 limitation
- [ ] Method chaining works: `s.trim().upper()`
- [ ] Global functions still work alongside methods
- [ ] ~85 new tests passing
- [ ] Updated `examples/frequency.qsr` using new methods

---

## 16. Timeline

| Week | Milestone                               |
| ---- | --------------------------------------- |
| 1    | Phase 11.0: Infrastructure complete     |
| 2    | Phase 11.1: String methods complete     |
| 3    | Phase 11.2: Collection methods complete |
| 4    | Testing, documentation, release v1.8.0  |

---

**Target Release:** v1.8.0 "Pulsar"

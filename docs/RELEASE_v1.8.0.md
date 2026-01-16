# 🌟 Quasar v1.8.0 "Pulsar" Release Notes

**Date:** 2026-01-16
**Codename:** Pulsar
**Focus:** Standard Library & Quality of Life
**Milestone:** 1,000+ Tests Passed 🏆

---

The **Pulsar** update brings the Quasar language to life with **Native Methods**. You can now manipulate primitive types using dot notation (`obj.method()`), making code significantly cleaner, more readable, and closer to modern programming standards.

## ✨ New Features

### 🧵 String Methods (Phase 11.1)

Manipulate text directly:

```quasar
let s: str = "  Hello World  "

print(s.len())              // 15
print(s.trim())             // "Hello World"
print(s.upper())            // "  HELLO WORLD  "
print(s.lower())            // "  hello world  "

let parts: [str] = s.trim().split(" ")  // ["Hello", "World"]
print(parts.join("-"))                   // "Hello-World"

print(s.contains("World"))   // true
print(s.starts_with("  H"))  // true
print(s.ends_with("  "))     // true

let num: str = "42"
let n: int = num.to_int()    // 42
let f: float = num.to_float() // 42.0
```

### 📚 List Methods (Phase 11.2)

Manage collections with OOP-style syntax:

```quasar
let nums: [int] = [1, 2, 3]

nums.push(4)                 // [1, 2, 3, 4]
let last: int = nums.pop()   // 4, nums = [1, 2, 3]

print(nums.contains(2))      // true
print(nums.len())            // 3

nums.reverse()               // [3, 2, 1]
nums.clear()                 // []

// Join for string lists
let words: [str] = ["a", "b", "c"]
print(words.join(","))       // "a,b,c"
```

### 🗺️ Dictionary Methods (Phase 11.2)

**Fixing the biggest usability gap from v1.7.0** — no more linear scanning!

```quasar
let scores: Dict[str, int] = {"Alice": 100, "Bob": 90}

// Key existence check (the #1 requested feature!)
if scores.has_key("Alice") {
    print("Alice is playing!")
}

// Safe access with default
let score: int = scores.get("Charlie", 0)  // Returns 0 if missing

// Mutation
scores.remove("Bob")
scores.clear()

// Iteration helpers
let keys: [str] = scores.keys()
let vals: [int] = scores.values()
print(keys.len())  // Method chaining works!
```

### 🛡️ Type Safety Improvements

Generic type validation ensures compile-time safety:

```quasar
let nums: [int] = [1, 2, 3]
nums.push("hello")  // ❌ E1100: expects element type 'int', got 'str'

let words: [int] = [1, 2, 3]
words.join(",")     // ❌ E1102: join() only works on [str]

let d: Dict[str, int] = {"a": 1}
d.get("b", "wrong") // ❌ E1100: expects value type 'int', got 'str'
```

## 🔧 Technical Changes

### New AST Node
- `MethodCallExpr(object, method, arguments, span)` — Represents `obj.method(args)`

### Primitive Method Registry
New architecture in the Semantic Analyzer:

```python
PRIMITIVE_METHODS = {
    "str":  {"len": ..., "upper": ..., "split": ...},
    "list": {"push": ..., "pop": ..., "contains": ...},
    "dict": {"has_key": ..., "get": ..., "keys": ...},
}
```

### Code Generation Mappings

| Quasar          | Python           |
| --------------- | ---------------- |
| `s.trim()`      | `s.strip()`      |
| `s.contains(x)` | `(x in s)`       |
| `l.push(v)`     | `l.append(v)`    |
| `l.join(sep)`   | `sep.join(l)`    |
| `d.has_key(k)`  | `(k in d)`       |
| `d.remove(k)`   | `d.pop(k, None)` |
| `d.keys()`      | `list(d.keys())` |

### New Error Codes

| Code  | Description                              |
| ----- | ---------------------------------------- |
| E1100 | Generic type mismatch in method argument |
| E1102 | `join()` called on non-string list       |
| E1105 | Method does not exist for type           |
| E1106 | Incorrect number of method arguments     |
| E1107 | Argument type mismatch                   |

## 📊 Stats

| Metric               | Value |
| -------------------- | ----- |
| **Total Tests**      | 1,022 |
| **Phase 11 Tests**   | 81    |
| **New Methods**      | 23    |
| **Breaking Changes** | 0     |

## ⬆️ Upgrade Guide

v1.8.0 is fully backward compatible with v1.7.0. No code changes required.

**Optional improvements:**
```quasar
// Old (v1.7.0)
let k: [str] = keys(scores)
let found: bool = false
for key in k {
    if key == "Alice" { found = true }
}

// New (v1.8.0) ✨
let found: bool = scores.has_key("Alice")
```

## 🔮 What's Next?

Phase 12 planning is underway. Candidates:
- **Pattern Matching** — `match` expressions
- **Enums** — Algebraic data types
- **Traits/Interfaces** — Polymorphism
- **Error Handling** — `Result<T, E>` types

---

**Full Changelog:** [v1.7.0...v1.8.0](https://github.com/JoaoGVTheodoro/quasar-lang/compare/v1.7.0...v1.8.0)

**Contributors:** João Gabriel Vieira Theodoro

---

<p align="center">
  <b>Quasar v1.8.0 "Pulsar"</b> — Methods that shine ✨
</p>

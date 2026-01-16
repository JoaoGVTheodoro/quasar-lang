# Release Notes — Quasar v1.7.0 "Supernova"

**Release Date:** 2026-01-15
**Codename:** Supernova
**Status:** Stable

---

## 🎉 Highlights

Quasar v1.7.0 introduces **Dictionaries** — the final core data structure, completing the language's collection types. Dictionaries provide efficient key-value mapping with static type safety.

### What's New

- **Dict Type:** `Dict[K, V]` — Statically-typed hash maps
- **Dict Literals:** `{ key: value }` syntax
- **Built-in Functions:** `keys()`, `values()`, extended `len()`
- **Type Safety:** Strict key/value type enforcement at compile time

---

## ✨ Features

### Dictionary Types

```quasar
let scores: Dict[str, int] = { "Alice": 100, "Bob": 90 }
let lookup: Dict[int, str] = { 1: "one", 2: "two" }
let empty: Dict[str, bool] = {}
```

**Key Type Restrictions:**
| Type        | Allowed as Key      |
| ----------- | ------------------- |
| `int`       | ✅ Yes               |
| `str`       | ✅ Yes               |
| `bool`      | ✅ Yes               |
| `float`     | ✅ Yes               |
| `[T]`       | ❌ No (not hashable) |
| `Dict[K,V]` | ❌ No (not hashable) |

### Index Operations

```quasar
# Read
let score: int = scores["Alice"]

# Write (update or insert)
scores["Alice"] = 105
scores["Eve"] = 80  # Creates new key
```

### Built-in Functions

```quasar
let d: Dict[str, int] = { "a": 1, "b": 2, "c": 3 }

# Length
print(len(d))         # 3

# Get all keys as list
let k: [str] = keys(d)

# Get all values as list
let v: [int] = values(d)
```

---

## 📊 Statistics

| Metric          | Value |
| --------------- | ----- |
| Tests Passing   | 941   |
| New Tests       | 56    |
| New Error Codes | 7     |
| New Built-ins   | 2     |

### New Error Codes

| Code  | Description                               |
| ----- | ----------------------------------------- |
| E1000 | Heterogeneous key types in dict literal   |
| E1001 | Heterogeneous value types in dict literal |
| E1002 | Non-hashable key type                     |
| E1003 | Dict key type mismatch                    |
| E1004 | Dict value type mismatch                  |
| E1005 | keys() argument must be dict              |
| E1006 | values() argument must be dict            |

---

## 📁 New Examples

### `examples/frequency.qsr`

Vote counting demonstration using dictionaries:

```quasar
let votes: [str] = ["blue", "red", "blue", "green"]
let counts: Dict[str, int] = {}

# Count votes
for i in 0..len(votes) {
    let vote: str = votes[i]
    # ... (see full example)
}

print("Blue: {}", counts["blue"])
```

---

## ⚠️ Known Limitations

1. **Key Existence Check:** No `haskey()` or `in` operator yet. Use `keys(d)` iteration as workaround.
2. **KeyError:** Reading missing key raises Python KeyError at runtime.
3. **No `.get()`:** Default value pattern not yet supported.

---

## 🔧 Technical Details

### Code Generation

| Quasar           | Python             |
| ---------------- | ------------------ |
| `Dict[str, int]` | `dict`             |
| `{ "a": 1 }`     | `{"a": 1}`         |
| `d["key"]`       | `d["key"]`         |
| `keys(d)`        | `list(d.keys())`   |
| `values(d)`      | `list(d.values())` |

### AST Changes

- `DictType`: Type node for `Dict[K, V]`
- `DictLiteral`: Expression node for `{ k: v }`
- `DictEntry`: Key-value pair node

---

## 📈 Upgrade Path

No breaking changes from v1.6.0. Existing code compiles without modification.

---

## 🗺️ What's Next

Potential future enhancements:
- `haskey(d, k)` — Check key existence
- `d.get(k, default)` — Safe access with default
- `for k, v in d { }` — Direct dict iteration
- `items(d)` — Key-value pairs as list

---

## 🙏 Acknowledgments

Thanks to the Quasar community for feedback and testing.

---

**Full Changelog:** v1.6.0...v1.7.0

---

<p align="center">
  <b>Quasar v1.7.0 "Supernova"</b> — Dictionaries are here! 🌟
</p>

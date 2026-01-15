# Quasar v1.6.0 Release Notes

**Release Date:** 2026-01-15  
**Codename:** Imports  
**Test Count:** 885

---

## 🎉 Highlights

This release introduces **Modules & Imports**, enabling Quasar programs to leverage Python's standard library and split code across multiple files.

---

## ✨ New Features

### Python Standard Library Imports
Access Python's stdlib modules directly:

```quasar
import math
import random

let x: float = math.sqrt(16.0)    // 4.0
let n: int = random.randint(1, 10)
```

### Local File Imports
Import other `.qsr` files:

```quasar
// main.qsr
import "./utils.qsr"

let h: float = utils.calculate(3.0, 4.0)
```

**Compiles to standard Python:**
```python
import math
import utils
```

### Multi-File Projects
Create modular projects with separate library and main files:

```
examples/multi_file_project/
├── utils.qsr    → utils.py
└── main.qsr     → main.py
```

Run with: `quasar compile *.qsr && python3 main.py`

### Dynamic Type Handling
Imported module members are treated as `any` type, allowing flexible interop:

```quasar
import math
let x: float = math.sqrt(4.0)    // Returns ANY, compatible with float
let y: int = math.floor(3.14)    // Returns ANY, compatible with int
```

---

## 📚 New Examples

| Example | Description |
|---------|-------------|
| `multi_file_project/` | Demonstrates Python + local imports |

---

## 🔧 Technical Changes

| Component | Change |
|-----------|--------|
| **Lexer** | Added `IMPORT` token |
| **AST** | Added `ImportDecl` node |
| **Parser** | `_flatten_member_access` for `module.func()` calls |
| **Semantic** | `ModuleSymbol`, `ANY` type, file existence check (E0901) |
| **CodeGen** | Transforms local paths to Python imports |

---

## ⚠️ Error Codes

| Code | Description |
|------|-------------|
| E0900 | Duplicate import |
| E0901 | Local module not found |

---

## 📊 Test Summary

| Phase | Tests |
|-------|-------|
| Phase 9.0 (Python imports) | 13 |
| Phase 9.1 (Local imports) | 18 |
| **Total Suite** | **885** |

---

## 🔄 Migration Notes

No breaking changes from v1.5.0. Existing code will work unchanged.

---

## 🔮 What's Next

- Methods on Structs (`fn Point.distance()`)
- Visibility modifiers (`pub`, `private`)
- Type stubs for Python stdlib

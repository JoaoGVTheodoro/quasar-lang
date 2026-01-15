# 🌟 Quasar

**Quasar** is a statically-typed programming language that compiles to Python. Designed for clarity and safety, it combines the simplicity of Python with the reliability of static type checking.

```quasar
import math
import "./utils.qsr"

let h: float = math.sqrt(16.0)
print("Result: {}", h)
```

**Status:** v1.6.0 — Phase 9 Complete ✅ (885 tests)

## ✨ Features

- **Modules & Imports** — Python stdlib + local `.qsr` files (v1.6.0)
- **User Defined Types** — Structs with dot notation
- **Lists & Ranges** — `[int]` arrays and `for i in 0..10` loops
- **Console I/O** — `print()` and `input()` builtins
- **Type Casting** — `int()`, `float()`, `str()`, `bool()`
- **Python Target** — Compiles to readable Python 3.10+

## 📦 Installation

```bash
git clone https://github.com/JoaoGVTheodoro/quasar-lang.git
cd quasar-lang
pip install .
```

```bash
quasar --version
# Output: Quasar 1.6.0
```

## 🚀 Usage

| Command                     | Description                    |
| --------------------------- | ------------------------------ |
| `quasar run <file.qsr>`     | Compile and execute            |
| `quasar compile <file.qsr>` | Compile to Python              |
| `quasar check <file.qsr>`   | Validate without generating    |

## 📖 Language Guide

### Imports (v1.6.0)

```quasar
import math                 // Python stdlib
import "./utils.qsr"        // Local file

let x: float = math.sqrt(16.0)
let y: int = utils.helper(5)
```

### Primitive Types

| Type    | Example              |
| ------- | -------------------- |
| `int`   | `42`, `-17`          |
| `float` | `3.14`, `-0.5`       |
| `bool`  | `true`, `false`      |
| `str`   | `"hello"`            |

### Variables & Constants

```quasar
let x: int = 10         // Mutable
const PI: float = 3.14  // Immutable
```

### Functions

```quasar
fn add(a: int, b: int) -> int {
    return a + b
}
```

### Control Flow

```quasar
if x > 0 {
    print("positive")
}

for i in 0..10 {
    print(i)
}
```

### Lists

```quasar
let nums: [int] = [1, 2, 3]
push(nums, 4)
print(len(nums))
```

### Structs

```quasar
struct Point { x: int, y: int }
let p: Point = Point { x: 0, y: 0 }
p.x = 100
```

### I/O

```quasar
print("Hello, {}", name)
let name: str = input()
```

## 🧪 Testing

```bash
pytest tests/ -v
# 885 tests passing
```

## 📁 Examples

| File | Description |
|------|-------------|
| `multi_file_project/` | Multi-file imports demo |
| `rpg.qsr` | RPG system with structs |
| `geometry.qsr` | Nested structs |

## 🗺️ Version History

| Version | Features |
|---------|----------|
| v1.0.0 | Core language |
| v1.1.0 | Print statement |
| v1.2.0 | Lists, ranges, for loops |
| v1.3.0 | List builtins |
| v1.4.0 | Input, type casting |
| v1.5.0 | Structs |
| **v1.6.0** | **Modules & Imports** |

## 📄 License

MIT License

## 👤 Author

**João Gabriel Vieira Theodoro** — [@JoaoGVTheodoro](https://github.com/JoaoGVTheodoro)

---

<p align="center">
  <b>Quasar</b> — Where static typing meets Python simplicity ⚡
</p>

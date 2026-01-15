# 🌟 Quasar

**Quasar** is a statically-typed programming language that compiles to Python. Designed for clarity and safety, it combines the simplicity of Python with the reliability of static type checking.

```quasar
struct Player { name: str, hp: int }

let hero: Player = Player { name: "Alice", hp: 100 }
hero.hp = hero.hp - 25
print("HP: {}", hero.hp)
```

**Status:** v1.5.0 — Phase 8 Complete ✅ (854 tests)

## ✨ Features

- **Static Type System** — Catch type errors at compile time
- **User Defined Types** — Structs with dot notation (v1.5.0)
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
# Output: Quasar 1.5.0
```

## 🚀 Usage

| Command                     | Description                    |
| --------------------------- | ------------------------------ |
| `quasar run <file.qsr>`     | Compile and execute            |
| `quasar compile <file.qsr>` | Compile to Python              |
| `quasar check <file.qsr>`   | Validate without generating    |

## 📖 Language Guide

### Primitive Types

| Type    | Example              |
| ------- | -------------------- |
| `int`   | `42`, `-17`          |
| `float` | `3.14`, `-0.5`       |
| `bool`  | `true`, `false`      |
| `str`   | `"hello"`            |

### Variables & Constants

```quasar
let x: int = 10       // Mutable
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
} else {
    print("non-positive")
}

while i < 10 {
    i = i + 1
}

for i in 0..10 {
    print(i)
}
```

### Lists

```quasar
let nums: [int] = [1, 2, 3]
nums[0] = 10
push(nums, 4)
print(len(nums))
```

### Structs (v1.5.0)

```quasar
struct Point { x: int, y: int }
struct Line { start: Point, finish: Point }

let p: Point = Point { x: 0, y: 0 }
let line: Line = Line { start: p, finish: Point { x: 10, y: 10 } }

// Deep access
let val: int = line.finish.x

// Modification
line.start.x = 100
```

### I/O

```quasar
print("Hello, World!")
print("Sum: {}", 1 + 2)

let name: str = input()
print("Hello, {}", name)
```

## 🏗️ Architecture

```
Source.qsr → Lexer → Parser → Semantic Analyzer → CodeGen → Python
```

## 🧪 Testing

```bash
pytest tests/ -v
# 854 tests passing
```

| Phase | Tests |
|-------|-------|
| Lexer | 97 |
| Parser | 93 |
| Semantic | 55+ |
| CodeGen | 80+ |
| Phase 6 (Lists) | 200+ |
| Phase 7 (I/O) | 100+ |
| Phase 8 (Structs) | 46 |
| **Total** | **854** |

## 📁 Examples

| File | Description |
|------|-------------|
| `examples/factorial.qsr` | Classic recursion |
| `examples/fibonacci.qsr` | Fibonacci sequence |
| `examples/rpg.qsr` | RPG system with structs |
| `examples/geometry.qsr` | Nested structs |

## 🗺️ Version History

| Version | Features |
|---------|----------|
| v1.0.0 | Core language (lexer, parser, semantic, codegen) |
| v1.1.0 | Print statement |
| v1.2.0 | Lists, ranges, for loops |
| v1.3.0 | List builtins (len, push, pop) |
| v1.4.0 | Input, type casting |
| **v1.5.0** | **User Defined Types (Structs)** |

## 📄 License

MIT License

## 👤 Author

**João Gabriel Vieira Theodoro** — [@JoaoGVTheodoro](https://github.com/JoaoGVTheodoro)

---

<p align="center">
  <b>Quasar</b> — Where static typing meets Python simplicity ⚡
</p>

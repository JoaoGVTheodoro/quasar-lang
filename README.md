# 🌟 Quasar

**Quasar** is a statically-typed programming language that compiles to Python. Designed for clarity and safety, it combines the simplicity of Python with the reliability of static type checking.

```
fn factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

let result: int = factorial(5)
print(result)
```

**Status:** v1.1.0 — Phase 5 Complete ✅

## ✨ Features

- **Static Type System** — Catch type errors at compile time, not runtime
- **Clean Syntax** — Familiar C-style syntax with modern touches
- **Python Target** — Compiles to readable, standard Python 3.10+
- **Fast Compilation** — Full pipeline in milliseconds
- **Comprehensive Errors** — Clear messages with exact source locations
- **Console Output** — Built-in `print()` for easy debugging (v1.1.0)

## 📦 Installation

### Requirements

- Python 3.10 or higher
- pip

### From Source

```bash
git clone https://github.com/JoaoGVTheodoro/quasar-lang.git
cd quasar-lang
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Verify Installation

```bash
quasar --version
# Output: Quasar 1.1.0
```

## 🚀 Usage

### CLI Commands

| Command                     | Description                               |
| --------------------------- | ----------------------------------------- |
| `quasar compile <file.qsr>` | Compile to Python (generates `<file>.py`) |
| `quasar run <file.qsr>`     | Compile and execute                       |
| `quasar check <file.qsr>`   | Validate without generating code          |
| `quasar --version`          | Show version                              |
| `quasar --help`             | Show help                                 |

### Examples

**Compile a file:**
```bash
quasar compile program.qsr
# ✓ Compiled: program.qsr → program.py
```

**Run directly:**
```bash
quasar run program.qsr
```

**Check for errors:**
```bash
quasar check program.qsr
# ✓ Valid: program.qsr
```

**Specify output file:**
```bash
quasar compile program.qsr -o output.py
```

## 📖 Language Guide

### Types

Quasar has four primitive types:

| Type    | Description            | Example              |
| ------- | ---------------------- | -------------------- |
| `int`   | Integer numbers        | `42`, `-17`, `0`     |
| `float` | Floating-point numbers | `3.14`, `-0.5`       |
| `bool`  | Boolean values         | `true`, `false`      |
| `str`   | Text strings           | `"hello"`, `"world"` |

### Variables

```
// Mutable variable
let x: int = 10
x = 20  // OK

// Immutable constant
const PI: float = 3.14159
// PI = 3.0  // Error: cannot reassign constant
```

### Functions

```
fn add(a: int, b: int) -> int {
    return a + b
}

fn greet(name: str) -> str {
    return "Hello, " + name
}

let sum: int = add(5, 3)
let message: str = greet("Quasar")
```

### Control Flow

**If/Else:**
```
fn abs(n: int) -> int {
    if n < 0 {
        return -n
    } else {
        return n
    }
}
```

**While Loop:**
```
fn countdown(n: int) -> int {
    let count: int = n
    while count > 0 {
        count = count - 1
    }
    return count
}
```

**Break and Continue:**
```
fn find_first_even(limit: int) -> int {
    let i: int = 1
    while i <= limit {
        if i % 2 == 0 {
            break
        }
        i = i + 1
    }
    return i
}
```

### Operators

**Arithmetic:**
| Operator | Description    |
| -------- | -------------- |
| `+`      | Addition       |
| `-`      | Subtraction    |
| `*`      | Multiplication |
| `/`      | Division       |
| `%`      | Modulo         |

**Comparison:**
| Operator | Description      |
| -------- | ---------------- |
| `==`     | Equal            |
| `!=`     | Not equal        |
| `<`      | Less than        |
| `>`      | Greater than     |
| `<=`     | Less or equal    |
| `>=`     | Greater or equal |

**Logical:**
| Quasar | Python | Description |
| ------ | ------ | ----------- |
| `&&`   | `and`  | Logical AND |
| `\|\|` | `or`   | Logical OR  |
| `!`    | `not`  | Logical NOT |

### Complete Example

```
// Fibonacci sequence
fn fib(n: int) -> int {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

// Calculate and print first 10 Fibonacci numbers
let i: int = 0
while i < 10 {
    print(fib(i))
    i = i + 1
}
```

## 🏗️ Architecture

Quasar follows a classic 4-phase compiler architecture:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   LEXER     │────▶│   PARSER    │────▶│  SEMANTIC   │────▶│  CODEGEN    │
│             │     │             │     │  ANALYZER   │     │             │
│ Source → Tokens   │ Tokens → AST│     │ Type Check  │     │ AST → Python│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     Phase 1            Phase 2            Phase 3            Phase 4
```

### Phase 1: Lexer
Converts source code into tokens. Handles keywords, operators, literals, and identifiers.

### Phase 2: Parser  
Transforms tokens into an Abstract Syntax Tree (AST). Implements recursive descent parsing.

### Phase 3: Semantic Analyzer
Validates the AST for type correctness, scope rules, and semantic constraints.

### Phase 4: Code Generator
Traverses the validated AST and emits equivalent Python source code.

## 🧪 Testing

Quasar has comprehensive test coverage across all phases:

```bash
# Run all tests
pytest tests/ -v

# Run specific phase tests
pytest tests/lexer/ -v      # 97 tests
pytest tests/parser/ -v     # 93 tests
pytest tests/semantic/ -v   # 55 tests
pytest tests/codegen/ -v    # 80 tests
pytest tests/cli/ -v        # 21 tests
pytest tests/e2e/ -v        # 20 tests
```

**Test Summary:**
| Component | Tests   | Status |
| --------- | ------- | ------ |
| Lexer     | 97      | ✅      |
| Parser    | 93      | ✅      |
| Semantic  | 55      | ✅      |
| CodeGen   | 80      | ✅      |
| CLI       | 21      | ✅      |
| E2E       | 20      | ✅      |
| **Total** | **366** | ✅      |

## 📁 Project Structure

```
quasar/
├── src/quasar/
│   ├── lexer/          # Tokenization
│   ├── parser/         # Syntax analysis
│   ├── ast/            # AST node definitions
│   ├── semantic/       # Type checking & validation
│   ├── codegen/        # Python code generation
│   └── cli/            # Command-line interface
├── tests/
│   ├── lexer/          # Lexer tests
│   ├── parser/         # Parser tests
│   ├── semantic/       # Semantic tests
│   ├── codegen/        # CodeGen tests
│   ├── cli/            # CLI tests
│   └── e2e/            # End-to-end tests
├── examples/           # Example Quasar programs
└── docs/               # Documentation
```

## 🗺️ Roadmap

### ✅ Completed (v1.0.0)

- [x] Phase 1: Lexer — Full tokenization
- [x] Phase 2: Parser — Complete AST generation
- [x] Phase 3: Semantic Analyzer — Type checking & scope validation
- [x] Phase 4: Code Generator — Python emission
- [x] CLI — compile/run/check commands

### ✅ Completed (v1.1.0)

- [x] Phase 5: `print()` builtin — Console output
- [x] 366 passing tests

### 🔜 Phase 5.1: Extended Builtins (Planned)

- [ ] `input()` — User input
- [ ] `len()` — Length of strings
- [ ] `str()`, `int()`, `float()` — Type conversions

### 🔮 Future Phases

- [ ] Arrays/Lists support
- [ ] For loops (`for i in range(n)`)
- [ ] Structs/Classes
- [ ] Module system (`import`)
- [ ] Pattern matching
- [ ] REPL mode

## 🤝 Contributing

Contributions are welcome! Please follow the TDD methodology:

1. Write tests first
2. Implement the feature
3. Ensure all 366+ tests pass
4. Submit a PR

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 👤 Author

**João Gabriel Vieira Theodoro**

- GitHub: [@JoaoGVTheodoro](https://github.com/JoaoGVTheodoro)

---

<p align="center">
  <b>Quasar</b> — Where static typing meets Python simplicity ⚡
</p>

## License

MIT

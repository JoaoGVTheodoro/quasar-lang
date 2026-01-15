# Changelog

All notable changes to Quasar will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] — 2025-01-15

### ✨ Added

- **Extended `print()` builtin** — Multiple arguments with sep/end parameters
  - Multiple positional arguments: `print(a, b, c)`
  - `sep` parameter: `print(a, b, sep=",")`
  - `end` parameter: `print(a, end="")`
  - Combined usage: `print(a, b, sep="-", end="!")`
  - Variable expressions for sep/end
  - 100% backward compatible with v1.1.0

- **New Lexer Tokens** — `SEP` and `END` keywords

- **Semantic Validation**
  - E0402: `sep` parameter must be type `str`
  - E0403: `end` parameter must be type `str`

### 📊 Test Summary

| Component | v1.1.0  | Added   | v1.2.0  |
| --------- | ------- | ------- | ------- |
| Lexer     | 97      | +6      | 103     |
| Parser    | 93      | +12     | 105     |
| Semantic  | 55      | +19     | 74      |
| CodeGen   | 80      | +15     | 95      |
| CLI       | 21      | —       | 21      |
| E2E       | 20      | +28     | 48      |
| **Total** | **366** | **+80** | **446** |

### 📁 New Files

- `tests/e2e/test_integration_print_ext.py` — Extended print E2E tests
- `docs/PHASE5_1_DESIGN.md` — Phase 5.1 design document (FROZEN)

### 🔧 Modified Files

- `src/quasar/lexer/token_type.py` — Added `SEP`, `END` tokens
- `src/quasar/ast/statements.py` — Updated `PrintStmt` dataclass
- `src/quasar/parser/parser.py` — Rewrote `_print_stmt()`
- `src/quasar/semantic/analyzer.py` — Added sep/end validation
- `src/quasar/codegen/generator.py` — Multi-arg generation

---

## [1.1.0] — 2025-01-15

### ✨ Added

- **`print()` builtin** — Console output for all primitive types
  - `print` is a keyword (cannot be shadowed)
  - Single argument: `print(expr)`
  - Supports: int, float, bool, str
  - Statement semantics (no return value)
  - Boolean mapping: `true` → `True`, `false` → `False`

- **End-to-End Test Suite** — 20 comprehensive E2E tests
  - Output validation with subprocess
  - Integration with functions and control flow
  - CLI interaction tests
  - Complex program tests (factorial, fibonacci)

### 📊 Test Summary

| Component | v1.0.0  | Added   | v1.1.0  |
| --------- | ------- | ------- | ------- |
| Lexer     | 93      | +4      | 97      |
| Parser    | 87      | +6      | 93      |
| Semantic  | 47      | +8      | 55      |
| CodeGen   | 68      | +12     | 80      |
| CLI       | 21      | —       | 21      |
| E2E       | 0       | +20     | 20      |
| **Total** | **316** | **+50** | **366** |

### 📁 New Files

- `tests/lexer/test_print.py` — Lexer tests for print keyword
- `tests/parser/test_print.py` — Parser tests for print statements
- `tests/semantic/test_print.py` — Semantic analyzer tests
- `tests/codegen/test_print.py` — Code generation tests
- `tests/e2e/test_print.py` — End-to-end integration tests
- `docs/PHASE5_DESIGN.md` — Phase 5 design document (FROZEN)

### 🔧 Modified Files

- `src/quasar/lexer/token_type.py` — Added `PRINT` token
- `src/quasar/ast/statements.py` — Added `PrintStmt` dataclass
- `src/quasar/ast/__init__.py` — Exported `PrintStmt`
- `src/quasar/parser/parser.py` — Added `_parse_print_stmt()`
- `src/quasar/semantic/analyzer.py` — Added `_analyze_print_stmt()`
- `src/quasar/codegen/generator.py` — Added `_generate_print_stmt()`

---

## [1.0.0] — 2025-01-14

### ✨ Initial Release

- **Phase 1: Lexer** — Full tokenization (93 tests)
- **Phase 2: Parser** — Complete AST generation (87 tests)
- **Phase 3: Semantic Analyzer** — Type checking & scope validation (47 tests)
- **Phase 4: Code Generator** — Python emission (68 tests)
- **CLI** — `compile`, `run`, `check` commands (21 tests)

### 🎯 Features

- Static type system with explicit types
- Four primitive types: int, float, bool, str
- Functions with explicit parameter/return types
- Control flow: if/else, while loops
- Arithmetic, comparison, and logical operators
- Clean C-style syntax
- Python 3.10+ code generation

---

[1.1.0]: https://github.com/quasar-lang/quasar/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/quasar-lang/quasar/releases/tag/v1.0.0

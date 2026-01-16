# Changelog

All notable changes to Quasar will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.9.1] — 2026-01-16 — "Prism Hardened"

### 🔒 Hardening

- **Return Path Analysis (E0303)**
  - Functions with non-void return types now require guaranteed return on all code paths
  - Conservative analysis: if/else with returns in both branches satisfies requirement
  - Loops are not considered guaranteed returns (may not execute)

- **Return Outside Function (E0304)**
  - Return statements at module level now produce semantic error
  - Previously silently ignored

### 📊 Test Summary

| Component  | v1.9.0   | Added    | v1.9.1   |
| ---------- | -------- | -------- | -------- |
| Hardening  | 25       | +12      | 37       |
| **Total**  | **1107** | **+12**  | **1119** |

---

## [1.9.0] — 2026-01-16 — "Prism"

### ✨ Added

- **Enums** — Named variant types
  - Declaration: `enum Color { Red, Green, Blue }`
  - Variant access: `Color.Red`
  - Type annotations: `let c: Color = Color.Red`
  - Equality comparison: `c == Color.Red`, `c != Color.Blue`
  - Function parameters and returns: `fn check(s: Status) -> bool`

- **AST Infrastructure**
  - New AST nodes: `EnumDecl`, `EnumVariant`
  - New type: `EnumType`
  - Parser: `_enum_decl()` with trailing comma support

- **Semantic Analysis**
  - Enum registry: `_defined_enums`
  - Type resolution: `_resolve_type()` for PrimitiveType → EnumType
  - Comparison validation for same-type enums only

- **Python Code Generation**
  - `from enum import Enum` import
  - `class Color(Enum):` with string-valued variants

- **New Error Codes**
  - E1200: Redeclaration of type (enum/struct conflict)
  - E1201: Duplicate variant in enum
  - E1202: Unknown variant access
  - E1204: Comparing different enum types
  - E1205: Relational operators (<, >, <=, >=) not allowed on enums

### 📊 Test Summary

| Component | v1.8.0   | Added   | v1.9.0   |
| --------- | -------- | ------- | -------- |
| Phase 12  | —        | +60     | 60       |
| **Total** | **1022** | **+60** | **1082** |

### 📁 New Files

- `tests/phase12/test_phase12_0_infrastructure.py` — 12 lexer/parser tests
- `tests/phase12/test_phase12_1_semantic.py` — 21 semantic tests
- `tests/phase12/test_phase12_2_codegen.py` — 14 codegen tests
- `tests/phase12/test_phase12_3_integration.py` — 13 E2E tests
- `docs/PHASE12_DESIGN.md` — Phase 12 design document (FROZEN)

### 🔧 Modified Files

- `src/quasar/lexer/token_type.py` — Added `ENUM` token
- `src/quasar/ast/declarations.py` — Added `EnumDecl`, `EnumVariant`
- `src/quasar/ast/types.py` — Added `EnumType`, updated `QuasarType`
- `src/quasar/ast/__init__.py` — Exported enum types
- `src/quasar/parser/parser.py` — Added `_enum_decl()`, `_enum_variant()`
- `src/quasar/semantic/analyzer.py` — Added `_analyze_enum_decl()`, `_resolve_type()`
- `src/quasar/codegen/generator.py` — Added `_generate_enum_decl()`

---


## [1.8.0] — 2026-01-16 — "Pulsar"

### ✨ Added

- **Native Methods** — Method syntax for built-in types
  - **String Methods (10):** `upper()`, `lower()`, `trim()`, `replace()`, `split()`, `contains()`, `starts_with()`, `ends_with()`, `to_int()`, `to_float()`
  - **List Methods (6):** `push()`, `pop()`, `contains()`, `join()`, `reverse()`, `clear()`
  - **Dict Methods (7):** `has_key()`, `get()`, `remove()`, `clear()`, `keys()`, `values()`

- **Method Call Infrastructure**
  - New AST node: `MethodCallExpr(object, method, arguments, span)`
  - Parser: DOT + IDENTIFIER + LPAREN → method call detection
  - Primitive Methods Registry with 23 method signatures
  - Generic type resolution for collection methods

- **Python-Idiomatic Code Generation**
  - `trim()` → `.strip()`
  - `contains(x)` → `(x in obj)`
  - `push(v)` → `.append(v)`
  - `join(sep)` → `sep.join(obj)` (inverted receiver)
  - `has_key(k)` → `(k in obj)`
  - `remove(k)` → `.pop(k, None)`
  - `keys()` → `list(obj.keys())`
  - `values()` → `list(obj.values())`

- **New Error Codes**
  - E1100: Generic type mismatch in method calls
  - E1102: join() only valid on [str] lists
  - E1105: Unknown method on type
  - E1106: Method argument count mismatch
  - E1107: Method argument type mismatch

### 📊 Test Summary

| Component | v1.7.0  | Added   | v1.8.0   |
| --------- | ------- | ------- | -------- |
| Phase 11  | —       | +81     | 81       |
| **Total** | **941** | **+81** | **1022** |

### 📁 New Files

- `tests/phase11/test_phase11_0_infrastructure.py` — 18 infrastructure tests
- `tests/phase11/test_phase11_1_string_methods.py` — 31 string method tests
- `tests/phase11/test_phase11_2_collection_methods.py` — 32 collection method tests
- `docs/PHASE11_DESIGN.md` — Phase 11 design document (FROZEN)
- `docs/RELEASE_v1.8.0.md` — Release notes

### 🔧 Modified Files

- `src/quasar/ast/expressions.py` — Added `MethodCallExpr` dataclass
- `src/quasar/ast/__init__.py` — Exported `MethodCallExpr`
- `src/quasar/parser/parser.py` — DOT handling with method call detection
- `src/quasar/semantic/analyzer.py` — `PRIMITIVE_METHODS` registry, `_get_method_call_expr_type()`
- `src/quasar/codegen/generator.py` — `_generate_method_call_expr()` with special mappings

---

## [1.7.0] — 2026-01-15 — "Supernova"

### ✨ Added

- **Dictionaries** — `Dict[K, V]` hash maps
  - Literal syntax: `{ "key": value }`
  - Type annotations: `Dict[str, int]`
  - Indexing: `d["key"]`, `d["key"] = value`
  - Builtins: `keys()`, `values()`, `len()`

### 📊 Test Summary

| Component | v1.6.0  | Added   | v1.7.0  |
| --------- | ------- | ------- | ------- |
| Phase 10  | —       | +86     | 86      |
| **Total** | **855** | **+86** | **941** |

---

## [1.6.0] — 2026-01-15 — "Entropy"

### ✨ Added

- **Modules & Imports** — Python stdlib + local .qsr files
  - `import math` — Python stdlib
  - `import "./utils.qsr"` — Local Quasar files
  - Namespace access: `math.sqrt()`, `utils.helper()`

---

## [1.5.0] — 2026-01-15 — "Light Speed"

### ✨ Added

- **Structs** — User-defined types
  - Declaration: `struct Point { x: int, y: int }`
  - Instantiation: `Point { x: 0, y: 0 }`
  - Member access: `p.x`, `p.x = 100`
  - Nested structs support

---

## [1.4.0] — 2026-01-15 — "Galaxy"

### ✨ Added

- **Console Input** — `input()` builtin
- **Type Casting** — `int()`, `float()`, `str()`, `bool()`

---

## [1.3.0] — 2026-01-15

### ✨ Added

- **Formatted Output (String Interpolation)** — `{}` placeholders in print statements
  - Basic interpolation: `print("Value: {}", x)`
  - Multiple placeholders: `print("{} + {} = {}", a, b, c)`
  - Works with all types: `int`, `float`, `bool`, `str`
  - Escape sequences: `{{` → `{`, `}}` → `}`
  - Integration with `end` parameter preserved
  - 100% backward compatible with v1.2.0

- **Semantic Validation**
  - E0410: Format string has more placeholders than arguments
  - E0411: Format string has fewer placeholders than arguments

- **Code Generation**
  - Format mode: `print("X={}".format(x))`
  - Normal mode preserved for non-format cases

### 📊 Test Summary

| Component | v1.2.0  | Added   | v1.3.0  |
| --------- | ------- | ------- | ------- |
| Lexer     | 103     | —       | 103     |
| Parser    | 105     | —       | 105     |
| Semantic  | 74      | +26     | 100     |
| CodeGen   | 95      | +23     | 118     |
| CLI       | 21      | —       | 21      |
| E2E       | 48      | +42     | 90      |
| **Total** | **446** | **+91** | **537** |

### 📁 New Files

- `tests/semantic/test_print_fmt.py` — Format string semantic tests
- `tests/codegen/test_print_fmt.py` — Format string codegen tests
- `tests/e2e/test_integration_print_fmt.py` — Format string E2E tests
- `docs/PHASE5_2_DESIGN.md` — Phase 5.2 design document (FROZEN)

### 🔧 Modified Files

- `src/quasar/semantic/analyzer.py` — Added format placeholder validation
- `src/quasar/codegen/generator.py` — Added `.format()` code generation

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

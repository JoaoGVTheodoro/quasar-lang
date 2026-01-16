# Quasar Language Invariants

This document defines architectural invariants that MUST be preserved across all future phases.
Violating these invariants is considered a regression, even if tests pass.

---

## 1. Lexer Invariants

### L-1: Context-Free Tokenization
The lexer operates without semantic context. Token classification depends ONLY on:
- Character sequences
- Keyword table lookup
- Position in source

**Never:** The lexer does not know about declared types, variables, or scope.

### L-2: Deterministic Token Stream
Given identical source code, the lexer produces identical token streams.
No randomness, no environment dependency.

### L-3: Complete Source Coverage
Every character in the source is accounted for in exactly one token (including whitespace tokens if emitted, or skipped explicitly).

---

## 2. Parser Invariants

### P-1: Context-Free Parsing
The parser builds AST from tokens without semantic knowledge.

**Never:**
- Parser does not check if types exist
- Parser does not check if variables are declared
- Parser does not resolve identifiers

### P-2: AST Completeness
Every valid token stream produces a complete AST or raises `ParserError`.
No partial ASTs are returned.

### P-3: Span Preservation
Every AST node contains a `span` field with accurate source location.
Spans are never synthesized or approximated.

### P-4: No Side Effects
Parsing is pure. Calling `parse()` twice on the same tokens produces identical ASTs.

---

## 3. Semantic Analyzer Invariants

### S-1: AST Preservation
The semantic analyzer NEVER creates, modifies, or deletes AST nodes.
It only reads the AST and raises errors.

**Input:** AST from parser  
**Output:** Same AST (unchanged) or `SemanticError`

### S-2: Single-Pass Analysis
Semantic analysis completes in a single pass over declarations.
No backtracking, no multi-pass resolution.

### S-3: Explicit Error Codes
Every semantic error has a unique code (E####) defined in documentation.
Error codes are never reused for different conditions.

### S-4: Type System Closure
Type checking uses only declared types:
- Primitive types: `int`, `float`, `bool`, `str`, `void`, `any`
- List types: `[T]`
- Dict types: `Dict[K, V]`
- User types: structs, enums

**Never:** Implicit type coercion between incompatible types.

### S-5: Scope Isolation
Variables declared in a scope are not visible outside that scope.
Function bodies, blocks, and loops create new scopes.

---

## 4. Code Generator Invariants

### C-1: Semantic Preservation
Generated Python code has IDENTICAL semantics to the Quasar source.
No optimizations that change observable behavior.

### C-2: Deterministic Output
Given identical AST, output is identical Python code.
No timestamps, random identifiers, or environment-dependent content.

### C-3: Valid Python
Generated code is always syntactically valid Python 3.10+.
If generation succeeds, `python -m py_compile` must pass.

### C-4: No Semantic Analysis
Code generator does NOT perform type checking or validation.
It trusts the AST has passed semantic analysis.

### C-5: Readable Output
Generated Python should be human-readable:
- Proper indentation
- Meaningful variable names (preserved from source)
- Standard idioms

---

## 5. Type System Invariants

### T-1: No Implicit Coercion
```quasar
let x: int = 3.14  // ERROR: cannot assign float to int
```
Explicit casting required: `int(3.14)`

### T-2: Homogeneous Collections
Lists contain elements of a single type:
```quasar
let nums: [int] = [1, 2, 3]     // OK
let mixed: [int] = [1, "two"]   // ERROR
```

### T-3: Function Return Guarantee
Every function with non-void return type returns a value on all code paths.

### T-4: Const Immutability
Constants cannot be reassigned after declaration:
```quasar
const PI: float = 3.14
PI = 3.0  // ERROR: cannot reassign constant
```

### T-5: Enum Type Safety
Enums are distinct types. Different enums cannot be compared or assigned:
```quasar
enum Color { Red }
enum Size { Big }
let c: Color = Size.Big  // ERROR: type mismatch
```

---

## 6. CLI Invariants

### CLI-1: Exit Codes
- `0`: Success
- `1`: Compilation error (syntax, semantic)
- `2`: Runtime error (execution failure)

### CLI-2: Deterministic Compilation
`quasar compile file.qsr` produces identical output across runs.

### CLI-3: No Hidden State
CLI commands do not depend on or modify persistent state.
No caches, no config files affecting behavior.

---

## 7. Testing Invariants

### TEST-1: Isolation
Each test is independent. Running tests in any order produces same results.

### TEST-2: No External Dependencies
Tests do not require network, external files, or specific environment.

### TEST-3: Error Code Verification
Tests for error conditions verify BOTH:
- Exception is raised
- Error code matches expected

---

## 8. Architectural Boundaries

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Lexer     │ →  │   Parser    │ →  │  Semantic   │ →  │  CodeGen    │
│             │    │             │    │  Analyzer   │    │             │
│ chars→tokens│    │ tokens→AST  │    │ AST→AST     │    │ AST→Python  │
│             │    │             │    │ (validate)  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      ↓                  ↓                  ↓                  ↓
   NO semantic       NO semantic       NO codegen         NO semantic
   knowledge         knowledge         NO AST changes     NO parsing
```

**Critical:** Information flows in ONE direction only. No component reaches back to a previous stage.

---

## 9. Future-Proofing

### FP-1: AST Extension Points
New features add new AST nodes. Existing nodes are never modified (only extended if inheritance is used).

### FP-2: Error Code Ranges
| Range | Feature |
|-------|---------|
| E0001-E0099 | Scope errors |
| E0100-E0199 | Type errors |
| E0200-E0299 | Control flow |
| E0400-E0499 | Print/IO |
| E0800-E0899 | Structs |
| E1100-E1199 | Methods |
| E1200-E1299 | Enums |
| E1300-E1399 | (Reserved: Pattern Matching) |

### FP-3: Keyword Stability
Once a keyword is added, it cannot be removed or repurposed.
Current keywords are FROZEN.

---

## Enforcement

These invariants are enforced by:
1. Code review (human verification)
2. Test coverage (automated)
3. Documentation (this file)

**Violation of any invariant requires explicit design review and documentation update.**

---

**Last Updated:** 2026-01-16  
**Version:** v1.9.0

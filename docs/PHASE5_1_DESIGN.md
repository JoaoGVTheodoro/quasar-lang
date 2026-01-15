# Phase 5.1 — Extended Print: Design Document

**Status:** ✅ FROZEN  
**Version:** 1.0.0  
**Date:** 2025-01-15  
**Completed:** 2025-01-15  
**Author:** Quasar Team  
**Depends On:** Phase 5.0 (FROZEN)

---

## 1. Executive Summary

Phase 5.1 extends the `print` builtin to support multiple arguments and optional `sep`/`end` parameters, aligning with Python's `print()` semantics while maintaining Quasar's static type system.

### Scope Definition

| In Scope                                      | Out of Scope                  |
| --------------------------------------------- | ----------------------------- |
| Multiple positional arguments                 | `file` parameter              |
| `sep` parameter (separator between arguments) | `flush` parameter             |
| `end` parameter (line terminator)             | Format specifiers / f-strings |
| Named parameter syntax for sep/end            | Variadic functions (general)  |
| Mixed types in single print                   | Print as expression (return)  |

### Backward Compatibility

✅ **100% backward compatible** — All existing `print(expr)` calls remain valid.

---

## 2. Design Decisions

### 2.1 Multiple Arguments Syntax

**Decision:** Comma-separated positional arguments

```
print(arg1, arg2, arg3)
print("Name:", name, "Age:", age)
print(a, b, c, sep=", ")
```

**Rationale:**
- Natural syntax familiar to Python/C developers
- No grammar ambiguity (comma already used in function calls)
- Enables practical patterns like labeled output

**Constraints:**
- Minimum 1 argument required (empty `print()` is invalid)
- Maximum 255 arguments (practical limit)
- All arguments must be printable types: `int`, `float`, `bool`, `str`

### 2.2 Named Parameters: `sep` and `end`

**Decision:** Support `sep` and `end` as **keyword-only** parameters

| Parameter | Type  | Default | Description                  |
| --------- | ----- | ------- | ---------------------------- |
| `sep`     | `str` | `" "`   | Separator between arguments  |
| `end`     | `str` | `"\n"`  | String appended after output |

**Syntax:**
```
print(a, b, c)                    // sep=" ", end="\n"
print(a, b, c, sep=", ")          // sep=", ", end="\n"
print(a, b, c, end="")            // sep=" ", end=""
print(a, b, c, sep="-", end="!\n") // sep="-", end="!\n"
```

**Rationale:**
- Matches Python semantics exactly
- Named parameters are explicit and readable
- `sep` and `end` are reserved for print only (not general named args)

**Constraints:**
- `sep` and `end` must be string literals or string variables
- Named parameters must come AFTER all positional arguments
- Order of `sep`/`end` is flexible: `sep=x, end=y` or `end=y, sep=x`
- Cannot repeat: `print(a, sep=",", sep=";")` is ERROR

### 2.3 Grammar Extension

**Current Grammar (Phase 5.0):**
```ebnf
print_stmt = "print" "(" expression ")" ;
```

**New Grammar (Phase 5.1):**
```ebnf
print_stmt      = "print" "(" print_args ")" ;
print_args      = expression ("," expression)* print_kwargs? ;
print_kwargs    = ("," print_kwarg)+ ;
print_kwarg     = ("sep" | "end") "=" expression ;
```

**Token Requirements:**
- `SEP` keyword token (new)
- `END` keyword token (new)
- Note: `=` already exists as `ASSIGN`

### 2.4 AST Changes

**Current PrintStmt:**
```python
@dataclass
class PrintStmt(Statement):
    expression: Expression
    span: Span
```

**New PrintStmt:**
```python
@dataclass
class PrintStmt(Statement):
    arguments: list[Expression]  # At least 1 element
    sep: Expression | None       # Must be str type if present
    end: Expression | None       # Must be str type if present
    span: Span
```

### 2.5 Semantic Rules

| Rule | Description                                            | Error Code |
| ---- | ------------------------------------------------------ | ---------- |
| R1   | Each argument must be `int`, `float`, `bool`, or `str` | E0401      |
| R2   | `sep` must be type `str` if provided                   | E0402      |
| R3   | `end` must be type `str` if provided                   | E0403      |
| R4   | Cannot have duplicate `sep` or `end`                   | E0404      |
| R5   | Named parameters must follow positional arguments      | E0405      |
| R6   | At least one positional argument required              | E0406      |

### 2.6 Code Generation

**Input:**
```
print(a, b, c, sep=", ", end="!\n")
```

**Output (Python):**
```python
print(a, b, c, sep=", ", end="!\n")
```

Direct 1:1 mapping to Python's print function.

---

## 3. Examples

### 3.1 Basic Multiple Arguments

```
// Quasar
let name: str = "Alice"
let age: int = 30
print("Name:", name, "Age:", age)

// Python Output
print("Name:", name, "Age:", age)

// Console Output
Name: Alice Age: 30
```

### 3.2 Custom Separator

```
// Quasar
print(1, 2, 3, 4, 5, sep=", ")

// Console Output
1, 2, 3, 4, 5
```

### 3.3 No Newline (Inline Output)

```
// Quasar
print("Loading", end="")
print(".", end="")
print(".", end="")
print(" Done!")

// Console Output
Loading.. Done!
```

### 3.4 CSV-Style Output

```
// Quasar
print("Name", "Age", "City", sep=",")
print("Alice", 30, "NYC", sep=",")
print("Bob", 25, "LA", sep=",")

// Console Output
Name,Age,City
Alice,30,NYC
Bob,25,LA
```

### 3.5 Mixed Types

```
// Quasar
let pi: float = 3.14159
let enabled: bool = true
print("Pi =", pi, "Enabled =", enabled)

// Console Output
Pi = 3.14159 Enabled = True
```

### 3.6 Factorial Example (Updated)

```
// Quasar
fn factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

let result: int = factorial(5)
print("Factorial =", result)

// Console Output
Factorial = 120
```

---

## 4. Error Messages

### E0401: Invalid argument type
```
print(some_function)
      ^^^^^^^^^^^^^ E0401: print argument must be int, float, bool, or str
```

### E0402: sep must be string
```
print(a, b, sep=42)
                ^^ E0402: 'sep' parameter must be type 'str', got 'int'
```

### E0403: end must be string
```
print(a, b, end=true)
                ^^^^ E0403: 'end' parameter must be type 'str', got 'bool'
```

### E0404: Duplicate parameter
```
print(a, sep=",", sep=";")
                  ^^^^^^^ E0404: duplicate 'sep' parameter
```

### E0405: Named after positional
```
print(sep=",", a, b)
               ^ E0405: positional argument after keyword argument
```

### E0406: Empty print
```
print()
^^^^^^^ E0406: print requires at least one argument
```

---

## 5. Implementation Plan

### Step 1: Lexer Updates
- Add `TokenType.SEP` for `sep` keyword
- Add `TokenType.END` for `end` keyword
- Update KEYWORDS dictionary
- **Tests:** 6 new tests

### Step 2: AST Updates
- Modify `PrintStmt` dataclass:
  - `expression` → `arguments: list[Expression]`
  - Add `sep: Expression | None`
  - Add `end: Expression | None`
- **Tests:** Existing tests must be updated

### Step 3: Parser Updates
- Rewrite `_parse_print_stmt()` for new grammar
- Parse multiple comma-separated expressions
- Parse optional `sep=` and `end=` parameters
- **Tests:** 12 new tests

### Step 4: Semantic Updates
- Update `_analyze_print_stmt()`:
  - Validate all arguments (loop)
  - Validate sep/end types
  - Check for duplicates
- Add error codes E0401-E0406
- **Tests:** 15 new tests

### Step 5: CodeGen Updates
- Update `_generate_print_stmt()`:
  - Generate comma-separated arguments
  - Emit sep/end if present
- **Tests:** 10 new tests

### Step 6: Integration Tests
- Update existing E2E tests
- Add multi-argument E2E tests
- Test sep/end combinations
- **Tests:** 15 new tests

### Test Budget

| Component | Current | Phase 5.1 | Total   |
| --------- | ------- | --------- | ------- |
| Lexer     | 97      | +6        | 103     |
| Parser    | 93      | +12       | 105     |
| Semantic  | 55      | +15       | 70      |
| CodeGen   | 80      | +10       | 90      |
| CLI       | 21      | —         | 21      |
| E2E       | 20      | +15       | 35      |
| **Total** | **366** | **+58**   | **424** |

---

## 6. Risk Assessment

| Risk                          | Probability | Impact | Mitigation                           |
| ----------------------------- | ----------- | ------ | ------------------------------------ |
| Breaking existing print tests | Medium      | High   | Update tests incrementally           |
| Grammar ambiguity with comma  | Low         | High   | sep/end are keyword-only             |
| Keyword collision (end)       | Low         | Medium | `end` reserved in print context only |

---

## 7. Open Questions

### Q1: Should `sep` and `end` be global keywords?

**Recommendation:** NO — Only recognized in print context

**Rationale:**
- `end` is common variable name
- Minimizes reserved word pollution
- Parser handles context-specifically

### Q2: Allow expressions for sep/end or literals only?

**Decision:** Allow any string expression

```
let separator: str = ", "
print(a, b, c, sep=separator)  // Valid
```

**Rationale:**
- More flexible
- Consistent with argument handling
- No additional complexity

### Q3: Support empty print()?

**Decision:** NO — Require at least one argument

**Rationale:**
- `print()` with no args is rare use case
- Can use `print("")` for blank line
- Simplifies grammar and validation

---

## 8. Acceptance Criteria

- [x] `print(a, b, c)` outputs `a b c\n`
- [x] `print(a, b, sep=",")` outputs `a,b\n`
- [x] `print(a, end="")` outputs `a` (no newline)
- [x] `print(a, b, sep="-", end="!\n")` outputs `a-b!\n`
- [x] All 366 existing tests still pass
- [x] 80 new tests for Phase 5.1 (exceeded target of 58)
- [x] Error messages for invalid usage (E0402, E0403)
- [x] examples/factorial.qsr runs correctly

---

## 9. Approval

| Role                | Name        | Date       | Signature  |
| ------------------- | ----------- | ---------- | ---------- |
| Design Lead         | Quasar Team | 2025-01-15 | ✅ Approved |
| Implementation Lead | Quasar Team | 2025-01-15 | ✅ Approved |

---

**Document Status:** ✅ FROZEN — Implementation complete.

---

## 10. Implementation Report

### Final Test Summary

| Component    | v1.1.0  | Phase 5.1 | v1.2.0  |
| ------------ | ------- | --------- | ------- |
| **Lexer**    | 97      | +6        | 103     |
| **Parser**   | 93      | +12       | 105     |
| **Semantic** | 55      | +19       | 74      |
| **CodeGen**  | 80      | +15       | 95      |
| **CLI**      | 21      | —         | 21      |
| **E2E**      | 20      | +28       | 48      |
| **Total**    | **366** | **+80**   | **446** |

### Features Delivered

- ✅ Multiple positional arguments: `print(a, b, c)`
- ✅ `sep` parameter: `print(a, b, sep=",")`
- ✅ `end` parameter: `print(a, end="")`
- ✅ Combined usage: `print(a, b, sep="-", end="!")`
- ✅ Variable expressions for sep/end
- ✅ Semantic validation: E0402, E0403

### Files Modified

- `src/quasar/lexer/token_type.py` — +SEP, +END tokens
- `src/quasar/ast/statements.py` — PrintStmt updated
- `src/quasar/parser/parser.py` — _print_stmt() rewritten
- `src/quasar/semantic/analyzer.py` — sep/end validation
- `src/quasar/codegen/generator.py` — multi-arg generation

### New Test Files

- `tests/e2e/test_integration_print_ext.py` (28 tests)

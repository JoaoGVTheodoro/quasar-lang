# Phase 5.2 — Formatted Output: Design Document

**Status:** ✅ FROZEN  
**Version:** 1.0.0  
**Date:** 2026-01-15  
**Author:** Quasar Team  
**Depends On:** Phase 5.1 (FROZEN)

---

## Final Test Report

| Component | v1.2.0  | Added   | v1.3.0  |
| --------- | ------- | ------- | ------- |
| Lexer     | 103     | —       | 103     |
| Parser    | 105     | —       | 105     |
| Semantic  | 74      | +26     | 100     |
| CodeGen   | 95      | +23     | 118     |
| CLI       | 21      | —       | 21      |
| E2E       | 48      | +42     | 90      |
| **Total** | **446** | **+91** | **537** |

---

## 1. Executive Summary

Phase 5.2 introduces "Formatted Output" capabilities to the existing `print` statement.
It allows the usage of `{}` placeholders within string literals to interpolate values.

### Scope Definition

| In Scope                                          | Out of Scope                      |
| ------------------------------------------------- | --------------------------------- |
| Placeholder syntax `{}` inside string literals    | Named placeholders `{name}`       |
| Positional matching of arguments                  | Indexed placeholders `{0}`, `{1}` |
| Validation of argument count vs placeholder count | Complex formatting `{:02d}`       |
| Integration with `sep` and `end`                  | String interpolation via `$var`   |
| Escape sequence `{{` and `}}`                     | Nested expressions `{x + y}`      |

### Backward Compatibility

✅ **100% backward compatible** — All existing `print` calls remain valid.

---

## 2. Design Decisions

### 2.1 Syntax Specification

**Decision:** Use Rust/Python-style `{}` braces as placeholders.

**Syntax:**
```quasar
print("Value: {}", x)
print("X: {}, Y: {}", x, y)
print("Name: {}, Age: {}", name, age)
```

**Rationale:**
- Familiar syntax from Python `.format()` and Rust `println!`
- Clear visual distinction from string content
- Minimal lexer changes (detect `{}` in strings)

### 2.2 Placeholder Resolution

**Decision:** Positional matching — placeholders are filled left-to-right.

**Rules:**
1. First `{}` → First argument after format string
2. Second `{}` → Second argument after format string
3. And so on...

**Example:**
```quasar
let a: int = 10
let b: int = 20
print("A={}, B={}", a, b)
// Output: A=10, B=20
```

### 2.3 Format String Detection

**Decision:** First argument with `{}` triggers format mode.

**Detection Logic:**
```
IF first_argument is StringLiteral AND contains "{}" THEN
    mode = FORMAT
ELSE
    mode = NORMAL (Phase 5.1 behavior)
```

**Examples:**
```quasar
// FORMAT mode (first arg has {})
print("Value: {}", 42)        // → "Value: 42"

// NORMAL mode (no {} in first arg)
print("Hello", "World")       // → "Hello World"
print(42)                     // → "42"
```

### 2.4 Escape Sequences

**Decision:** `{{` produces `{` and `}}` produces `}`

**Syntax:**
```quasar
print("Use {{}} for placeholders")
// Output: Use {} for placeholders

print("JSON: {{{}}}", value)
// Output: JSON: {42}
```

### 2.5 Argument Count Validation

**Decision:** Strict validation — placeholder count MUST equal argument count.

| Scenario                 | Behavior                    |
| ------------------------ | --------------------------- |
| Placeholders = Arguments | ✅ Valid                     |
| Placeholders > Arguments | ❌ E0410: Too few arguments  |
| Placeholders < Arguments | ❌ E0411: Too many arguments |

**Examples:**
```quasar
print("X={}, Y={}", 1, 2)      // ✅ Valid (2 == 2)
print("X={}, Y={}", 1)         // ❌ E0410: expected 2 args, got 1
print("X={}", 1, 2, 3)         // ❌ E0411: expected 1 arg, got 3
```

### 2.6 Integration with sep/end

**Decision:** `sep` and `end` work AFTER format resolution.

**Behavior:**
- Format string is resolved first
- Result is treated as single "formatted" argument
- `sep` only applies if there are additional non-format arguments
- `end` applies normally

**Examples:**
```quasar
print("X={}", 10, end="!")
// Output: X=10!

print("Result: {}", 42, "extra", sep=" | ")
// Output: Result: 42 | extra
```

### 2.7 Type Handling in Placeholders

**Decision:** Same type handling as Phase 5.1.

| Type  | Format                 |
| ----- | ---------------------- |
| int   | Decimal representation |
| float | Decimal representation |
| bool  | `True` / `False`       |
| str   | Raw string value       |

---

## 3. Grammar Changes

### Current Grammar (Phase 5.1):
```ebnf
print_stmt      = "print" "(" print_args ")" ;
print_args      = expression ("," expression)* print_kwargs? ;
```

### New Grammar (Phase 5.2):
```ebnf
print_stmt      = "print" "(" print_args ")" ;
print_args      = expression ("," expression)* print_kwargs? ;

(* No grammar change — format detection is semantic *)
```

**Note:** Grammar remains unchanged. Format detection happens during semantic analysis by inspecting the first argument.

---

## 4. Implementation Strategy

### 4.1 Lexer Changes

**None required.** The `{}` characters are already valid inside string literals.

### 4.2 Parser Changes

**None required.** The parser already handles multiple arguments.

### 4.3 AST Changes

**Option A: No AST changes** (recommended)
- Format detection happens in semantic phase
- CodeGen inspects first argument for `{}`

**Option B: Add format flag to PrintStmt**
```python
@dataclass
class PrintStmt(Statement):
    arguments: list[Expression]
    sep: Expression | None
    end: Expression | None
    is_format: bool  # NEW
    span: Span
```

**Recommendation:** Option A — Keep AST unchanged, handle in CodeGen.

### 4.4 Semantic Changes

Add validation for format strings:

```python
def _analyze_print_stmt(self, stmt: PrintStmt) -> None:
    # ... existing validation ...
    
    # Check for format string
    if self._is_format_string(stmt.arguments[0]):
        placeholder_count = self._count_placeholders(stmt.arguments[0])
        arg_count = len(stmt.arguments) - 1  # Exclude format string
        
        if placeholder_count > arg_count:
            raise SemanticError(
                code="E0410",
                message=f"format string has {placeholder_count} placeholders but only {arg_count} arguments provided",
                span=stmt.span,
            )
        
        if placeholder_count < arg_count:
            raise SemanticError(
                code="E0411",
                message=f"format string has {placeholder_count} placeholders but {arg_count} arguments provided",
                span=stmt.span,
            )
```

### 4.5 CodeGen Changes

**Output Strategy:** Generate Python `.format()` call.

```python
def _generate_print_stmt(self, stmt: PrintStmt) -> None:
    first_arg = stmt.arguments[0]
    
    if self._is_format_string(first_arg):
        # Format mode
        format_str = self._generate_expression(first_arg)
        format_args = [self._generate_expression(arg) for arg in stmt.arguments[1:]]
        result = f"{format_str}.format({', '.join(format_args)})"
        self._emit(f"print({result})")
    else:
        # Normal mode (Phase 5.1)
        # ... existing code ...
```

**Example Transformations:**

| Quasar                       | Python                              |
| ---------------------------- | ----------------------------------- |
| `print("X={}", 10)`          | `print("X={}".format(10))`          |
| `print("A={}, B={}", a, b)`  | `print("A={}, B={}".format(a, b))`  |
| `print("X={}", 10, end="!")` | `print("X={}".format(10), end="!")` |

---

## 5. Examples

### 5.1 Basic Formatting

```quasar
let name: str = "Alice"
let age: int = 30
print("Name: {}, Age: {}", name, age)
```
**Output:** `Name: Alice, Age: 30`

### 5.2 Numeric Formatting

```quasar
let pi: float = 3.14159
print("Pi = {}", pi)
```
**Output:** `Pi = 3.14159`

### 5.3 Boolean Formatting

```quasar
let enabled: bool = true
print("Enabled: {}", enabled)
```
**Output:** `Enabled: True`

### 5.4 Multiple Values

```quasar
print("({}, {}, {})", 1, 2, 3)
```
**Output:** `(1, 2, 3)`

### 5.5 Escaped Braces

```quasar
print("Use {{}} for format")
```
**Output:** `Use {} for format`

### 5.6 With end Parameter

```quasar
print("Loading: {}%", 50, end="\r")
```
**Output:** `Loading: 50%` (with carriage return)

### 5.7 Mixed Mode

```quasar
print("Result: {}", result, "extra info")
```
**Output:** `Result: 42 extra info`

---

## 6. Error Messages

### E0410: Too few arguments for format string
```
print("X={}, Y={}", 1)
                    ^ E0410: format string has 2 placeholders but only 1 argument provided
```

### E0411: Too many arguments for format string
```
print("X={}", 1, 2, 3)
              ^^^^^^^ E0411: format string has 1 placeholder but 3 arguments provided
```

---

## 7. Test Plan

### 7.1 Semantic Tests (8 tests)
- `test_format_single_placeholder_valid`
- `test_format_multiple_placeholders_valid`
- `test_format_too_few_args_E0410`
- `test_format_too_many_args_E0411`
- `test_format_escaped_braces_valid`
- `test_format_with_sep_valid`
- `test_format_with_end_valid`
- `test_format_no_placeholders_normal_mode`

### 7.2 CodeGen Tests (8 tests)
- `test_codegen_format_single`
- `test_codegen_format_multiple`
- `test_codegen_format_escaped`
- `test_codegen_format_with_end`
- `test_codegen_format_mixed_types`
- `test_codegen_format_bool_true`
- `test_codegen_format_bool_false`
- `test_codegen_format_float`

### 7.3 E2E Tests (8 tests)
- `test_e2e_format_basic`
- `test_e2e_format_multiple_values`
- `test_e2e_format_escaped_braces`
- `test_e2e_format_with_function`
- `test_e2e_format_in_loop`
- `test_e2e_format_with_end`
- `test_e2e_format_progress_bar`
- `test_e2e_format_table_row`

### Test Budget

| Component | v1.2.0  | Phase 5.2 | Target  |
| --------- | ------- | --------- | ------- |
| Lexer     | 103     | +0        | 103     |
| Parser    | 105     | +0        | 105     |
| Semantic  | 74      | +8        | 82      |
| CodeGen   | 95      | +8        | 103     |
| CLI       | 21      | +0        | 21      |
| E2E       | 48      | +8        | 56      |
| **Total** | **446** | **+24**   | **470** |

---

## 8. Risk Assessment

| Risk                          | Probability | Impact | Mitigation                         |
| ----------------------------- | ----------- | ------ | ---------------------------------- |
| Breaking existing print tests | Low         | High   | Format mode only when `{}` present |
| Ambiguity with literal `{}`   | Low         | Medium | Escape sequence `{{}}`             |
| Complex nested scenarios      | Medium      | Low    | Out of scope for Phase 5.2         |

---

## 9. Open Questions

### Q1: Should empty `{}` be allowed in normal strings?

**Decision:** YES — `{}` is only special if there are arguments after the string.

```quasar
print("{}")              // Output: {} (no args, literal string)
print("{}", 42)          // Output: 42 (format mode)
```

### Q2: What if format string is a variable?

**Decision:** NOT SUPPORTED in Phase 5.2 — Only string literals.

```quasar
let fmt: str = "X={}"
print(fmt, 42)           // Output: X={} 42 (normal mode, not format)
```

**Rationale:** Compile-time validation requires literal string inspection.

---

## 10. Acceptance Criteria

- [ ] `print("X={}", 10)` outputs `X=10`
- [ ] `print("A={}, B={}", 1, 2)` outputs `A=1, B=2`
- [ ] `print("Use {{}}")` outputs `Use {}`
- [ ] `print("X={}", 1, end="!")` outputs `X=1!`
- [ ] E0410 raised for too few arguments
- [ ] E0411 raised for too many arguments
- [ ] All 446 existing tests still pass
- [ ] 24+ new tests for Phase 5.2

---

## 11. Approval

| Role                | Name | Date | Signature |
| ------------------- | ---- | ---- | --------- |
| Design Lead         | —    | —    | ☐ Pending |
| Implementation Lead | —    | —    | ☐ Pending |

---

**Document Status:** Awaiting approval to proceed to IMPLEMENTATION MODE.

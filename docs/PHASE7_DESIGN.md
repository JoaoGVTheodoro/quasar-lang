# Phase 7 — Interactivity & Type Casting: Design Document

**Status:** ✅ FROZEN
**Version:** 1.4.0
**Date:** 2026-01-15
**Author:** Quasar Team
**Depends On:** Phase 6 (FROZEN, v1.3.0)
**Tests Passing:** 808

---

## 1. Executive Summary

Phase 7 introduces **user input** via `input()` and **explicit type conversion** (casting) functions. This enables Quasar programs to interact with users and process external data.

### Motivation

Currently, Quasar programs are "deaf" — they cannot receive data from the outside world. All values must be hardcoded. Phase 7 addresses this limitation by:

1. Adding `input()` for reading user input from stdin
2. Adding type casting functions (`int()`, `float()`, `str()`, `bool()`) for converting between types

### Scope Definition

| In Scope                        | Out of Scope                     |
| ------------------------------- | -------------------------------- |
| `input(prompt)` built-in        | File I/O (`read_file`, `write`)  |
| `int(value)` conversion         | Exception handling (`try/catch`) |
| `float(value)` conversion       | Custom error types               |
| `str(value)` conversion         | Input validation helpers         |
| `bool(value)` conversion        | Type inference from input        |
| Runtime errors on invalid input | Nullable/Optional types          |

### Backward Compatibility

✅ **100% backward compatible** — All existing Quasar programs remain valid.

---

## 2. Design Decisions

### 2.1 The `input()` Built-in

**Decision:** Add `input()` as a built-in function that reads a line from stdin.

**Signature:**
```quasar
fn input() -> str
fn input(prompt: str) -> str
```

**Behavior:**
- With no arguments: Reads a line from stdin, returns as `str`
- With prompt argument: Displays prompt, then reads input

**Examples:**
```quasar
# Without prompt
let name: str = input()

# With prompt
let age_str: str = input("Enter your age: ")

# Chained with conversion
let age: int = int(input("Enter your age: "))
```

**Code Generation:**
```python
# input() → input()
# input("prompt") → input("prompt")
name = input()
age_str = input("Enter your age: ")
```

**Design Rationale:**

| Option                 | Pros                  | Cons                     |
| ---------------------- | --------------------- | ------------------------ |
| Required prompt        | Consistent API        | Verbose for simple cases |
| Optional prompt        | Flexible, Python-like | Slight complexity        |
| Separate `read_line()` | Clear naming          | Different from Python    |

**Choice: Optional prompt** — Matches Python semantics exactly, familiar to users.

### 2.2 Type Casting Functions

**Decision:** Add four type casting functions as built-ins.

**Signatures:**
```quasar
fn int(value: any) -> int
fn float(value: any) -> float
fn str(value: any) -> str
fn bool(value: any) -> bool
```

**Note:** The `any` type here is a semantic concept — these functions accept any Quasar type and attempt conversion at runtime.

**Valid Conversions:**

| From / To | `int()`      | `float()`      | `str()`           | `bool()`        |
| --------- | ------------ | -------------- | ----------------- | --------------- |
| `int`     | ✅ identity   | ✅ `1 → 1.0`    | ✅ `1 → "1"`       | ✅ `0 → false`   |
| `float`   | ✅ truncate   | ✅ identity     | ✅ `1.5 → "1.5"`   | ✅ `0.0 → false` |
| `str`     | ✅ parse      | ✅ parse        | ✅ identity        | ✅ `"" → false`  |
| `bool`    | ✅ `true → 1` | ✅ `true → 1.0` | ✅ `true → "True"` | ✅ identity      |

**Examples:**
```quasar
# String to numeric
let x: int = int("42")           # 42
let y: float = float("3.14")     # 3.14

# Numeric to string
let s: str = str(100)            # "100"

# Boolean conversions
let b: bool = bool(1)            # true
let n: int = int(true)           # 1

# From input (common pattern)
let age: int = int(input("Age: "))
let price: float = float(input("Price: "))
```

**Code Generation:**
```python
# Direct 1:1 mapping
x = int("42")
y = float("3.14")
s = str(100)
b = bool(1)
```

### 2.3 Semantic Analysis Strategy

**Decision:** Permissive at compile-time, fail at runtime.

**Rationale:**
Since Quasar doesn't have exception handling yet, and Python's type constructors already validate input, we delegate validation to Python runtime.

**Semantic Rules:**

1. `input()` — Accept 0 or 1 string argument
2. `int()`, `float()`, `str()`, `bool()` — Accept exactly 1 argument of any type

**Error Codes:**

| Code  | Description                                    |
| ----- | ---------------------------------------------- |
| E0600 | `input()` wrong argument count (max 1)         |
| E0601 | `input()` argument must be string              |
| E0602 | Cast function wrong argument count (exactly 1) |

**What we DON'T check at compile-time:**
- Whether `int("abc")` will succeed (runtime error)
- Whether the conversion makes semantic sense

### 2.4 Runtime Error Behavior

**Decision:** Allow Python exceptions to propagate (crash the program).

**Rationale:**
Without `try/catch`, there's no way to handle errors gracefully. The pragmatic approach is to let Python's exceptions bubble up naturally.

**Example Runtime Errors:**
```quasar
let x: int = int("abc")    # Python ValueError: invalid literal
let y: int = int(input())  # ValueError if user enters non-numeric
```

**Error Message (from Python):**
```
ValueError: invalid literal for int() with base 10: 'abc'
```

**Future Phase:** Phase 8+ may introduce `try/catch` for error handling.

---

## 3. Implementation Plan

### 3.1 Sub-Phase Breakdown

| Sub-Phase | Description            | Estimated Tests |
| --------- | ---------------------- | --------------- |
| 7.0       | `input()` built-in     | 10              |
| 7.1       | Type casting functions | 25              |
| 7.2       | Integration & E2E      | 10              |
| **Total** |                        | **~45**         |

### 3.2 Phase 7.0 — `input()` Built-in

**Lexer:** No changes (input is intercepted as identifier, like `len`/`push`)

**Parser:** No changes (parsed as `CallExpr`)

**Semantic Analyzer:**
```python
def _check_builtin_input(self, expr: CallExpr) -> QuasarType:
    """Validate input() call."""
    if len(expr.arguments) > 1:
        raise SemanticError(
            code="E0600",
            message="input() takes at most 1 argument",
            span=expr.span,
        )
    if len(expr.arguments) == 1:
        arg_type = self._get_expression_type(expr.arguments[0])
        if arg_type != STR:
            raise SemanticError(
                code="E0601",
                message=f"input() prompt must be str, got {arg_type}",
                span=expr.arguments[0].span,
            )
    return STR  # Always returns string
```

**Code Generator:**
```python
# input() → input()
# input("prompt") → input("prompt")
if expr.callee == "input":
    if len(expr.arguments) == 0:
        return "input()"
    else:
        prompt = self._generate_expression(expr.arguments[0])
        return f"input({prompt})"
```

### 3.3 Phase 7.1 — Type Casting Functions

**Semantic Analyzer:**
```python
CAST_FUNCTIONS = {"int", "float", "str", "bool"}

def _check_builtin_cast(self, expr: CallExpr) -> QuasarType:
    """Validate type casting function call."""
    if len(expr.arguments) != 1:
        raise SemanticError(
            code="E0602",
            message=f"{expr.callee}() requires exactly 1 argument",
            span=expr.span,
        )
    # Validate the argument (ensures it's a valid expression)
    self._get_expression_type(expr.arguments[0])
    
    # Return the target type
    return {
        "int": INT,
        "float": FLOAT,
        "str": STR,
        "bool": BOOL,
    }[expr.callee]
```

**Code Generator:**
```python
# Direct 1:1 mapping
if expr.callee in {"int", "float", "str", "bool"}:
    arg = self._generate_expression(expr.arguments[0])
    return f"{expr.callee}({arg})"
```

---

## 4. Grammar Changes

No grammar changes required. All new features use existing `CallExpr` syntax.

```
call → primary ( "(" arg_list? ")" | "[" expression "]" )*
```

The built-ins `input`, `int`, `float`, `str`, `bool` are intercepted at semantic analysis, similar to `len` and `push`.

---

## 5. Test Plan

### 5.1 Phase 7.0 Tests — `input()`

```python
# Semantic: Valid usage
test_input_no_args()           # input()
test_input_with_prompt()       # input("Name: ")
test_input_type_is_str()       # let x: str = input()

# Semantic: Errors
test_input_too_many_args()     # input("a", "b") → E0600
test_input_non_string_prompt() # input(42) → E0601

# CodeGen
test_codegen_input_no_args()   # → input()
test_codegen_input_with_prompt() # → input("Name: ")
```

### 5.2 Phase 7.1 Tests — Type Casting

```python
# int() conversions
test_int_from_string()         # int("42")
test_int_from_float()          # int(3.14)
test_int_from_bool()           # int(true)
test_int_from_int()            # int(42) - identity

# float() conversions
test_float_from_string()       # float("3.14")
test_float_from_int()          # float(42)
test_float_from_bool()         # float(true)

# str() conversions
test_str_from_int()            # str(42)
test_str_from_float()          # str(3.14)
test_str_from_bool()           # str(true)

# bool() conversions
test_bool_from_int()           # bool(0), bool(1)
test_bool_from_string()        # bool(""), bool("x")

# Errors
test_cast_no_args()            # int() → E0602
test_cast_too_many_args()      # int(1, 2) → E0602

# CodeGen
test_codegen_int()             # → int(x)
test_codegen_float()           # → float(x)
test_codegen_str()             # → str(x)
test_codegen_bool()            # → bool(x)
```

### 5.3 Phase 7.2 Tests — Integration

```python
# Combined usage patterns
test_input_to_int()            # int(input())
test_input_to_float()          # float(input("Price: "))
test_calculator_program()      # Full interactive program
test_type_chain()              # str(int(float("3.14")))
```

---

## 6. Example Programs

### 6.1 Simple Calculator

```quasar
# calculator.qsr - Interactive calculator
print("=== Quasar Calculator ===")

let a: int = int(input("Enter first number: "))
let b: int = int(input("Enter second number: "))

print("{} + {} = {}", a, b, a + b)
print("{} - {} = {}", a, b, a - b)
print("{} * {} = {}", a, b, a * b)
print("{} / {} = {}", a, b, a / b)
```

### 6.2 Temperature Converter

```quasar
# temperature.qsr - Celsius to Fahrenheit
let celsius: float = float(input("Enter temperature in Celsius: "))
let fahrenheit: float = celsius * 1.8 + 32.0
print("{} C = {} F", celsius, fahrenheit)
```

### 6.3 Number Guessing Game

```quasar
# guess.qsr - Simple guessing game
let secret: int = 42
let attempts: int = 0

print("Guess the number (1-100)!")

for i in 0..10 {
    let guess: int = int(input("Your guess: "))
    attempts = attempts + 1
    
    if guess == secret {
        print("Correct! You got it in {} attempts.", attempts)
        break
    } else {
        if guess < secret {
            print("Too low!")
        } else {
            print("Too high!")
        }
    }
}
```

---

## 7. Risk Analysis

| Risk                                             | Impact | Mitigation                                        |
| ------------------------------------------------ | ------ | ------------------------------------------------- |
| Invalid input crashes program                    | Medium | Document as expected behavior; future `try/catch` |
| `int`/`float`/`str`/`bool` shadow user functions | Low    | These are reserved built-ins (like `len`, `push`) |
| Interactive tests are hard to automate           | Medium | Use mock stdin in test framework                  |

---

## 8. Future Considerations

### Phase 8+ Candidates

1. **Exception Handling** — `try/catch/finally` for graceful error recovery
2. **Input Validation Helpers** — `is_numeric(str)`, `parse_int_or_default()`
3. **File I/O** — `read_file()`, `write_file()`
4. **Command-line Arguments** — `args: [str]`

---

## 9. Acceptance Criteria

- [ ] `input()` works with 0 or 1 string argument
- [ ] `int()`, `float()`, `str()`, `bool()` work with any single argument
- [ ] Semantic errors E0600, E0601, E0602 are enforced
- [ ] Code generation produces correct Python
- [ ] ~45 new tests pass
- [ ] Example programs run correctly
- [ ] Total test count: 719 + 45 = ~764

---

## 10. Sign-off

| Role                | Name | Date | Signature |
| ------------------- | ---- | ---- | --------- |
| Design Lead         |      |      |           |
| Implementation Lead |      |      |           |
| QA Lead             |      |      |           |

---

**End of Document**

# Release v1.4.0

## Overview
**Version:** v1.4.0
**Date:** 2026-01-15
**Status:** Stable
**Tests:** 808 Passing

This release marks the completion of **Phase 7** (I/O & Casting) and includes a critical hotfix for binary operator precedence.

## 🚀 New Features

### 1. Interactive Input (`input()`)
The `input()` built-in function allows reading string input from standard input (stdin).
```javascript
let name: str = input("What's your name? ")
print("Hello, {}", name)
```

### 2. Type Casting
Added support for explicit type conversion between primitive types using constructor-like syntax:
- `int(x)`: Converts strings/floats/bools to integer.
- `float(x)`: Converts strings/ints/bools to float.
- `str(x)`: Converts any primitive to string.
- `bool(x)`: Converts strings ("true"/"false") or numbers to boolean.

```javascript
let age_str: str = "30"
let age: int = int(age_str)
```

## 🐛 Bug Fixes

### Critical: Precedence Hotfix
Fixed a code generation issue where binary operations were concatenated without grouping, leading to incorrect evaluation order in Python.
- **Before:** `(2 + 3) * 4` -> generated `2 + 3 * 4` (equals 14)
- **Fixed:** `(2 + 3) * 4` -> generates `(2 + 3) * 4` (equals 20)

**Implementation:** The code generator now applies defensive parentheses around all binary expressions to guarantee correct precedence preservation.

## 📈 Quality Metrics
- **Total Tests:** 808
- **Test Coverage:** All Phase 7 features + Hotfix Regression Suite.

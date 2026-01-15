# Quasar v1.3.0 Release Notes

**Release Date:** 2026-01-15  
**Status:** Stable  
**Tests:** 719 passing

---

## 🎉 Overview

Quasar v1.3.0 introduces **Phase 6 — Data Structures & Control Flow**, the most significant update since the initial release. This version adds first-class support for lists, iterators, and modern control flow constructs.

---

## ✨ New Features

### Lists & Arrays

Quasar now supports homogeneous list types with full type inference:

```quasar
# Simple lists
let numbers: [int] = [1, 2, 3, 4, 5]
let names: [str] = ["Alice", "Bob", "Charlie"]

# Nested lists (matrices)
let matrix: [[int]] = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

# Empty lists (type annotation required)
let empty: [float] = []
```

**Type Safety:**
- All list elements must be the same type (homogeneous)
- Compile-time type checking for list operations
- Error E0500: Heterogeneous list detection

### Index Access & Mutation

Zero-based indexing with bracket notation:

```quasar
let nums: [int] = [10, 20, 30]

# Read access
let first: int = nums[0]      # 10
let last: int = nums[2]       # 30

# Write access (mutation)
nums[0] = 100                 # nums is now [100, 20, 30]

# Chained access for nested lists
let val: int = matrix[1][2]   # 6
matrix[0][0] = 99             # Modify nested element
```

**Type Safety:**
- Error E0501: Index must be int
- Error E0502: Can only index list types
- Error E0503: Assignment type must match element type

### Built-in Functions

Two essential list operations:

```quasar
# len(list) → int
let count: int = len(numbers)   # 5

# push(list, value) → void
push(numbers, 6)                # numbers is now [1,2,3,4,5,6]
```

**Type Safety:**
- Error E0506: push() requires list and compatible value
- Error E0507: len() requires exactly one list argument

### For Loops

Iterator-based loops with automatic type inference:

```quasar
# Iterate over list elements
for item in numbers {
    print(item)
}

# Loop variable type is inferred
for name in names {           # name: str
    print("Hello, {}!", name)
}

# Nested loops for matrices
for row in matrix {           # row: [int]
    for cell in row {         # cell: int
        print(cell)
    }
}
```

### Range Expressions

Exclusive ranges for numeric iteration:

```quasar
# Range syntax: start..end (end is exclusive)
for i in 0..10 {              # i = 0, 1, 2, ..., 9
    print(i)
}

# Use with len() for index-based iteration
for i in 0..len(numbers) {
    print("Index {}: {}", i, numbers[i])
}

# Dynamic ranges
let n: int = 5
for i in 1..n + 1 {           # i = 1, 2, 3, 4, 5
    print(i)
}
```

**Type Safety:**
- Error E0504: Range bounds must be int
- Error E0505: Cannot iterate over non-iterable types

### Format Strings (Phase 5.2)

String interpolation with `{}` placeholders:

```quasar
let name: str = "World"
let count: int = 42

print("Hello, {}!", name)           # Hello, World!
print("Count: {}", count)           # Count: 42
print("{} + {} = {}", 1, 2, 1 + 2)  # 1 + 2 = 3
```

---

## 📁 Example Programs

Three example programs are included in `examples/`:

| File            | Description                                             |
| --------------- | ------------------------------------------------------- |
| `fibonacci.qsr` | Fibonacci sequence generator using lists and loops      |
| `primes.qsr`    | Prime number finder using nested loops and conditionals |
| `matrix.qsr`    | Matrix operations demonstrating 2D array manipulation   |

Run examples:
```bash
quasar run examples/fibonacci.qsr
quasar run examples/primes.qsr
quasar run examples/matrix.qsr
```

---

## 🧪 Test Coverage

| Component                | Tests   |
| ------------------------ | ------- |
| Phase 6.0 — Type System  | 46      |
| Phase 6.1 — Index Access | 34      |
| Phase 6.2 — Built-ins    | 30      |
| Phase 6.3 — For Loops    | 39      |
| Phase 6.4 — Integration  | 33      |
| Previous Phases          | 537     |
| **Total**                | **719** |

---

## 🔧 Technical Changes

### New Tokens
- `FOR` — for loop keyword
- `IN` — iterator keyword
- `DOTDOT` (`..`) — range operator

### New AST Nodes
- `ListLiteral` — `[1, 2, 3]`
- `IndexExpr` — `list[i]`
- `IndexAssignStmt` — `list[i] = val`
- `RangeExpr` — `start..end`
- `ForStmt` — `for x in iter { }`

### New Type System
- `ListType(element_type)` — Parameterized list type
- Type inference for list literals
- Empty list handling with `VOID` placeholder

### New Error Codes
| Code  | Description                      |
| ----- | -------------------------------- |
| E0500 | Heterogeneous list elements      |
| E0501 | Index must be int                |
| E0502 | Cannot index non-list type       |
| E0503 | Index assignment type mismatch   |
| E0504 | Range bounds must be int         |
| E0505 | Cannot iterate over non-iterable |
| E0506 | push() argument error            |
| E0507 | len() argument error             |

---

## 📈 Performance

Code generation remains efficient:
- Lists → Python lists (native)
- Ranges → Python `range()` (lazy evaluation)
- Index access → Python `[]` operator
- No runtime overhead

---

## 🔮 What's Next

Phase 7 (tentative):
- Function expressions / lambdas
- Higher-order functions
- Pattern matching

---

## 🙏 Acknowledgments

Thank you to all contributors and testers who helped make Phase 6 a reality.

**Quasar v1.3.0 — Building the future, one phase at a time.**

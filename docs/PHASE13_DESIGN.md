# Phase 13 — System Interaction (I/O & Env)

**Status:** FROZEN
**Target Version:** v1.10.0
**Codename:** "Script"

---

## 1. Overview

Phase 13 transforms Quasar from a pure algorithmic language into a practical scripting language capable of interacting with the operating system. This phase introduces two native static objects: `File` and `Env`.

### Design Philosophy

| Principle            | Decision                                        |
| -------------------- | ----------------------------------------------- |
| No new syntax        | Exposed as static method calls                  |
| No new types         | Uses existing `str`, `int`, `bool`, `[str]`     |
| No custom errors     | I/O failures crash with Python exceptions       |
| Python as backend    | We accept runtime failure as the trade-off      |
| UTF-8 everywhere     | All file operations use explicit UTF-8 encoding |
| Reserved identifiers | `File` and `Env` cannot be shadowed             |

---

## 2. API: File System (`File`)

A static object for file operations.

### Methods

| Method   | Signature                                      | Description                |
| -------- | ---------------------------------------------- | -------------------------- |
| `read`   | `File.read(path: str) -> str`                  | Read entire file as string |
| `write`  | `File.write(path: str, content: str) -> void`  | Overwrite file             |
| `append` | `File.append(path: str, content: str) -> void` | Append to file             |
| `exists` | `File.exists(path: str) -> bool`               | Check if path exists       |
| `delete` | `File.delete(path: str) -> void`               | Remove file                |

### Examples

```quasar
// Read a file
let content: str = File.read("data.txt")
print(content)

// Write a file
File.write("output.txt", "Hello, World!")

// Check existence before reading
if File.exists("config.txt") {
    let config: str = File.read("config.txt")
}

// Append to log
File.append("log.txt", "New entry\n")
```

### Error Behavior

| Scenario              | Behavior                   |
| --------------------- | -------------------------- |
| File not found (read) | Python `FileNotFoundError` |
| Permission denied     | Python `PermissionError`   |
| Invalid path          | Python `OSError`           |

---

## 3. API: Environment (`Env`)

A static object for environment variables and process context.

### Methods

| Method | Signature                                | Description                   |
| ------ | ---------------------------------------- | ----------------------------- |
| `get`  | `Env.get(key: str, default: str) -> str` | Get env var with default      |
| `set`  | `Env.set(key: str, value: str) -> void`  | Set env var (current process) |
| `args` | `Env.args() -> [str]`                    | Command line arguments        |
| `cwd`  | `Env.cwd() -> str`                       | Current working directory     |

### Examples

```quasar
// Get environment variable with safe default
let home: str = Env.get("HOME", "/tmp")
let port: str = Env.get("PORT", "8080")

// Command line arguments
let args: [str] = Env.args()
if args.len() > 1 {
    print("First arg: {}", args[1])
}

// Current directory
let cwd: str = Env.cwd()
print("Running from: {}", cwd)
```

### Design Decision: Required Default

> [!IMPORTANT]
> `Env.get(key, default)` **requires** a default value. `Env.get(key)` is NOT valid.

Rationale:
- Avoids crash on missing keys
- Forces explicit handling of absent variables
- Consistent with Quasar's "no nulls" philosophy

---

## 4. Amendments (QC Review)

The following amendments are **mandatory** and were added after QC review:

### 4.1 UTF-8 Everywhere (Previsibilidade)

All file operations MUST use explicit `encoding='utf-8'`.

**Generated Python:**
```python
# Correct
open(path, 'r', encoding='utf-8').read()

# NOT acceptable
open(path, 'r').read()
```

**Justification:** Avoids cross-platform encoding bugs (Windows cp1252 vs Linux utf-8).

### 4.2 Protected Identifiers (E0205)

`File` and `Env` are **reserved identifiers**. They cannot be shadowed.

**Prohibited:**
```quasar
let File: int = 1         // E0205
struct Env { }            // E0205
fn File() -> void { }     // E0205
fn test(File: int) { }    // E0205
```

**New Error Code:**
```
E0205: cannot shadow builtin module 'File'
```

### 4.3 Default Parameter Enforcement

`Env.get(key, default)` requires exactly 2 arguments. Semantic analyzer rejects single-argument calls.

---

## 5. Technical Implementation

### 5.1 Semantic Analyzer Changes

**New Registry:** `_static_objects`

```python
self._static_objects = {
    "File": {
        "read": StaticMethodSignature(params=[STR], return_type=STR),
        "write": StaticMethodSignature(params=[STR, STR], return_type=VOID),
        "append": StaticMethodSignature(params=[STR, STR], return_type=VOID),
        "exists": StaticMethodSignature(params=[STR], return_type=BOOL),
        "delete": StaticMethodSignature(params=[STR], return_type=VOID),
    },
    "Env": {
        "get": StaticMethodSignature(params=[STR, STR], return_type=STR),
        "set": StaticMethodSignature(params=[STR, STR], return_type=VOID),
        "args": StaticMethodSignature(params=[], return_type=ListType(STR)),
        "cwd": StaticMethodSignature(params=[], return_type=STR),
    }
}
```

**Shadowing Check:** In `_analyze_var_decl`, `_analyze_struct_decl`, `_analyze_fn_decl`:
- If name is in `_static_objects`, raise E0205

**Detection:** In `_get_member_access_expr_type`:
1. Check if object is `Identifier` with name in `_static_objects`
2. Validate method name exists
3. Return static method type

### 5.2 Code Generator Changes

**Imports Added:**
```python
import os
import sys
```

**Method Mappings (with UTF-8):**

| Quasar              | Python                                    |
| ------------------- | ----------------------------------------- |
| `File.read(p)`      | `open(p, 'r', encoding='utf-8').read()`   |
| `File.write(p, c)`  | `open(p, 'w', encoding='utf-8').write(c)` |
| `File.append(p, c)` | `open(p, 'a', encoding='utf-8').write(c)` |
| `File.exists(p)`    | `os.path.exists(p)`                       |
| `File.delete(p)`    | `os.remove(p)`                            |
| `Env.get(k, d)`     | `os.environ.get(k, d)`                    |
| `Env.set(k, v)`     | `os.environ[k] = v`                       |
| `Env.args()`        | `sys.argv`                                |
| `Env.cwd()`         | `os.getcwd()`                             |

---

## 6. Implementation Phases

### Phase 13.0: Infrastructure
- [ ] Register `File` and `Env` as static objects in semantic analyzer
- [ ] Add E0205 shadowing protection
- [ ] Add `os` and `sys` imports to code generator
- [ ] Add infrastructure tests

### Phase 13.1: File API
- [ ] Implement `File.read`, `File.write`, `File.append`
- [ ] Implement `File.exists`, `File.delete`
- [ ] Add integration tests

### Phase 13.2: Env API
- [ ] Implement `Env.get`, `Env.set`
- [ ] Implement `Env.args`, `Env.cwd`
- [ ] Add integration tests

---

## 7. Error Codes

| Code  | Message                               | Trigger                          |
| ----- | ------------------------------------- | -------------------------------- |
| E0205 | cannot shadow builtin module '{name}' | `let File = ...` or `struct Env` |

---

## 8. Test Plan

### Phase 13.0 Tests (~10)

1. **E0205:** `let File: int = 1` (variable shadowing)
2. **E0205:** `struct Env {}` (struct shadowing)
3. **E0205:** `fn File() {}` (function shadowing)
4. **E0205:** `fn test(File: int) {}` (parameter shadowing)
5. **Valid:** `File.exists("path")` recognized
6. **Valid:** `Env.cwd()` recognized
7. **CodeGen:** `import os` present
8. **CodeGen:** `import sys` present
9. **Error:** `File.unknown()` invalid method
10. **Error:** `Env.get("key")` missing default

### Integration Tests (Phase 13.1-13.2)
- File read/write roundtrip
- UTF-8 encoding verification
- Environment variable manipulation
- Command line argument access

---

## 9. CHANGELOG Entry (Preview)

```markdown
## [1.10.0] — TBD — "Script"

### ✨ Added

- **File System API** (`File` static object)
  - `File.read(path)`, `File.write(path, content)`, `File.append(path, content)`
  - `File.exists(path)`, `File.delete(path)`
  - All operations use UTF-8 encoding

- **Environment API** (`Env` static object)
  - `Env.get(key, default)`, `Env.set(key, value)`
  - `Env.args()`, `Env.cwd()`

- **New Error Code**
  - E0205: cannot shadow builtin module
```

---

## 10. Architectural Compliance

| Check                | Status                |
| -------------------- | --------------------- |
| No new syntax        | ✅ Static method calls |
| No generics          | ✅ Fixed signatures    |
| No pattern matching  | ✅ Not required        |
| No custom errors     | ✅ Python exceptions   |
| Existing types only  | ✅ str, bool, [str]    |
| UTF-8 encoding       | ✅ Mandatory           |
| Reserved identifiers | ✅ E0205 protection    |

---

**Document Status:** FROZEN

## 11. Implementation Hardening (moved)

Implementation details for Phase 13 hardening are maintained in a separate document: `docs/PHASE13_HARDENING.md`.

> Note: Hardening work (namespace aliasing, defensive copying of `Env.args`, static object protection E0205) is targeted for **v1.10.1** to allow independent review and traceability.
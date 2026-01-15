# Phase 5 — Builtin Functions: Design Document

**Status:** DRAFT  
**Version:** 0.1.0  
**Date:** 2026-01-15  
**Author:** Quasar Team  

---

## 1. Executive Summary

Phase 5 introduces the first builtin function to Quasar: `print`. This phase has a deliberately **minimal scope** to maintain stability while enabling basic I/O capabilities essential for practical programs.

### Scope Definition

| In Scope                                    | Out of Scope                        |
| ------------------------------------------- | ----------------------------------- |
| `print(expr)` single argument               | `print(a, b, c)` multiple arguments |
| All primitive types (int, float, bool, str) | Formatted strings, f-strings        |
| Statement form (no return value)            | Expression form (returning value)   |
| Newline-terminated output                   | Custom separators/terminators       |

---

## 2. Design Decisions

### 2.1 Is `print` a Keyword or Special Identifier?

**Decision:** `print` is a **KEYWORD**

**Rationale:**
- Prevents users from shadowing `print` with variable/function names
- Consistent with Quasar's philosophy of explicit semantics
- Simplifies parsing (no ambiguity with function calls)
- Aligns with the treatment in many languages (Python 2, BASIC, etc.)

**Implications:**
- Lexer must recognize `print` as `TokenType.PRINT`
- Cannot declare `let print: int = 5` (syntax error)
- Cannot define `fn print() -> int { ... }` (syntax error)

### 2.2 Does `print` Accept Multiple Arguments?

**Decision:** NO — Single argument only in Phase 5

**Rationale:**
- Minimizes complexity for initial implementation
- Avoids grammar ambiguity with comma expressions
- Multiple arguments can be simulated: `print(a)` then `print(b)`
- Can be extended in Phase 5.1 if needed

**Future Extension Path:**
```
// Phase 5.0 (current)
print(x)

// Phase 5.1 (future, if approved)
print(x, y, z)
```

### 2.3 Does `print` Accept Complex Expressions?

**Decision:** YES — Any valid expression

**Rationale:**
- Consistent with Quasar's expression-based design
- Enables useful patterns: `print(factorial(5))`, `print(2 + 3)`
- No additional parser complexity (reuses existing expression parsing)

**Valid Examples:**
```
print(42)                    // literal
print(x)                     // variable
print(x + y)                 // binary expression
print(factorial(5))          // function call
print(x > 0 && y < 10)       // logical expression
print("hello" + " world")    // string concatenation
```

### 2.4 How is `print` Treated in the Type System?

**Decision:** `print` is a **STATEMENT** with **VOID semantics**

**Rationale:**
- `print` produces a side effect (console output), not a value
- Cannot be used in expressions: `let x: int = print(5)` is INVALID
- Consistent with imperative I/O semantics

**Type Rules:**
| Rule | Description                                                     |
| ---- | --------------------------------------------------------------- |
| R1   | `print(expr)` where `expr: T` and `T ∈ {int, float, bool, str}` |
| R2   | `print(expr)` is a statement, not an expression                 |
| R3   | `print(expr)` cannot appear in expression context               |

### 2.5 Output Format Specification

**Decision:** Type-aware formatting matching Python semantics

| Quasar Type | Example Input    | Python Output |
| ----------- | ---------------- | ------------- |
| `int`       | `print(42)`      | `42`          |
| `float`     | `print(3.14)`    | `3.14`        |
| `bool`      | `print(true)`    | `True`        |
| `bool`      | `print(false)`   | `False`       |
| `str`       | `print("hello")` | `hello`       |

**Note:** Strings are printed WITHOUT quotes (standard behavior).

---

## 3. Grammar Changes (Phase 1 — Lexer)

### 3.1 New Token

```
TokenType.PRINT = "print"
```

### 3.2 Updated Keyword List

```python
KEYWORDS = {
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "fn": TokenType.FN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "return": TokenType.RETURN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "int": TokenType.INT_TYPE,
    "float": TokenType.FLOAT_TYPE,
    "bool": TokenType.BOOL_TYPE,
    "str": TokenType.STR_TYPE,
    "print": TokenType.PRINT,      # NEW
}
```

### 3.3 EBNF Grammar Update

```ebnf
(* Existing *)
statement → varDecl
          | constDecl
          | fnDecl
          | ifStmt
          | whileStmt
          | returnStmt
          | breakStmt
          | continueStmt
          | assignStmt
          | exprStmt
          | printStmt          (* NEW *)

(* NEW *)
printStmt → "print" "(" expression ")" NEWLINE
```

---

## 4. AST Changes (Phase 2 — Parser)

### 4.1 New AST Node

```python
@dataclass
class PrintStmt(Statement):
    """
    Print statement node.
    
    Represents: print(expression)
    
    Attributes:
        expression: The expression to print
        span: Source location
    """
    expression: Expression
    span: Span
```

### 4.2 AST Hierarchy (Updated)

```
Node
├── Program
├── Declaration
│   ├── VarDecl
│   ├── ConstDecl
│   └── FnDecl
├── Statement
│   ├── IfStmt
│   ├── WhileStmt
│   ├── ReturnStmt
│   ├── BreakStmt
│   ├── ContinueStmt
│   ├── AssignStmt
│   ├── ExprStmt
│   └── PrintStmt          ← NEW
└── Expression
    └── (unchanged)
```

### 4.3 Parser Modification

```python
def _parse_statement(self) -> Statement:
    if self._check(TokenType.PRINT):
        return self._parse_print_stmt()
    # ... existing statement parsing
```

```python
def _parse_print_stmt(self) -> PrintStmt:
    """
    printStmt → "print" "(" expression ")"
    """
    start = self._current_token().span
    self._expect(TokenType.PRINT)
    self._expect(TokenType.LPAREN)
    expr = self._parse_expression()
    self._expect(TokenType.RPAREN)
    
    return PrintStmt(
        expression=expr,
        span=Span.merge(start, self._previous_token().span)
    )
```

---

## 5. Semantic Changes (Phase 3 — Analyzer)

### 5.1 Type Checking Rule

```python
def _analyze_print_stmt(self, stmt: PrintStmt) -> None:
    """
    Validate print statement.
    
    Rules:
    1. Expression must be valid
    2. Expression type must be primitive (int, float, bool, str)
    """
    expr_type = self._analyze_expression(stmt.expression)
    
    PRINTABLE_TYPES = {
        Type.INT,
        Type.FLOAT,
        Type.BOOL,
        Type.STR,
    }
    
    if expr_type not in PRINTABLE_TYPES:
        raise SemanticError(
            code="E0400",
            message=f"cannot print value of type '{expr_type}'",
            span=stmt.expression.span
        )
```

### 5.2 New Error Code

| Code  | Message                               | Description                           |
| ----- | ------------------------------------- | ------------------------------------- |
| E0400 | `cannot print value of type '{type}'` | Attempted to print non-primitive type |

**Note:** E0400 is reserved for future use when non-primitive types exist. In Phase 5, all existing types are printable, so this error cannot occur. However, the check is implemented for forward compatibility.

### 5.3 No New Scope Rules

`print` does not:
- Introduce a new scope
- Declare any variables
- Affect control flow

---

## 6. CodeGen Changes (Phase 4 — Generator)

### 6.1 Code Generation Rule

```python
def _generate_print_stmt(self, stmt: PrintStmt) -> str:
    """
    Generate Python print statement.
    
    Quasar: print(expr)
    Python: print(expr)
    """
    expr_code = self._generate_expression(stmt.expression)
    return f"print({expr_code})"
```

### 6.2 Boolean Conversion

Boolean literals are already converted by expression generation:
- `true` → `True`
- `false` → `False`

### 6.3 Examples

| Quasar Source         | Generated Python      |
| --------------------- | --------------------- |
| `print(42)`           | `print(42)`           |
| `print(3.14)`         | `print(3.14)`         |
| `print(true)`         | `print(True)`         |
| `print(false)`        | `print(False)`        |
| `print("hello")`      | `print("hello")`      |
| `print(x + y)`        | `print(x + y)`        |
| `print(factorial(5))` | `print(factorial(5))` |

---

## 7. Test Specification

### 7.1 Test Categories

| Category    | Count  | Description       |
| ----------- | ------ | ----------------- |
| Lexer       | 4      | Token recognition |
| Parser      | 6      | AST construction  |
| Semantic    | 4      | Type validation   |
| CodeGen     | 8      | Python generation |
| Integration | 3      | End-to-end        |
| **Total**   | **25** |                   |

### 7.2 Lexer Tests (4)

```python
# test_lexer_print.py

def test_print_keyword_recognized():
    """print should be tokenized as PRINT keyword"""
    tokens = tokenize("print")
    assert tokens[0].type == TokenType.PRINT

def test_print_in_statement():
    """print in context should be recognized"""
    tokens = tokenize("print(42)")
    assert tokens[0].type == TokenType.PRINT
    assert tokens[1].type == TokenType.LPAREN
    assert tokens[2].type == TokenType.INT_LITERAL
    assert tokens[3].type == TokenType.RPAREN

def test_print_not_identifier():
    """print should NOT be an identifier"""
    tokens = tokenize("print")
    assert tokens[0].type != TokenType.IDENTIFIER

def test_print_case_sensitive():
    """PRINT, Print should be identifiers, not keywords"""
    tokens = tokenize("PRINT Print")
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[1].type == TokenType.IDENTIFIER
```

### 7.3 Parser Tests (6)

```python
# test_parser_print.py

def test_parse_print_int_literal():
    """Should parse print(42)"""
    ast = parse("print(42)")
    stmt = ast.declarations[0]
    assert isinstance(stmt, PrintStmt)
    assert isinstance(stmt.expression, IntLiteral)
    assert stmt.expression.value == 42

def test_parse_print_string_literal():
    """Should parse print("hello")"""
    ast = parse('print("hello")')
    stmt = ast.declarations[0]
    assert isinstance(stmt, PrintStmt)
    assert isinstance(stmt.expression, StrLiteral)

def test_parse_print_variable():
    """Should parse print(x)"""
    ast = parse("let x: int = 5\nprint(x)")
    stmt = ast.declarations[1]
    assert isinstance(stmt, PrintStmt)
    assert isinstance(stmt.expression, Identifier)

def test_parse_print_binary_expr():
    """Should parse print(2 + 3)"""
    ast = parse("print(2 + 3)")
    stmt = ast.declarations[0]
    assert isinstance(stmt, PrintStmt)
    assert isinstance(stmt.expression, BinaryExpr)

def test_parse_print_function_call():
    """Should parse print(f(x))"""
    source = """fn double(n: int) -> int {
    return n * 2
}
print(double(5))"""
    ast = parse(source)
    stmt = ast.declarations[1]
    assert isinstance(stmt, PrintStmt)
    assert isinstance(stmt.expression, CallExpr)

def test_parse_print_missing_paren_error():
    """Should error on print 42 (missing parens)"""
    with pytest.raises(ParserError):
        parse("print 42")
```

### 7.4 Semantic Tests (4)

```python
# test_semantic_print.py

def test_print_int_valid():
    """print(int) should be valid"""
    analyze("print(42)")  # No error

def test_print_float_valid():
    """print(float) should be valid"""
    analyze("print(3.14)")  # No error

def test_print_bool_valid():
    """print(bool) should be valid"""
    analyze("print(true)")  # No error

def test_print_str_valid():
    """print(str) should be valid"""
    analyze('print("hello")')  # No error
```

### 7.5 CodeGen Tests (8)

```python
# test_codegen_print.py

def test_codegen_print_int():
    """print(42) → print(42)"""
    code = generate("print(42)")
    assert code == "print(42)"

def test_codegen_print_float():
    """print(3.14) → print(3.14)"""
    code = generate("print(3.14)")
    assert code == "print(3.14)"

def test_codegen_print_true():
    """print(true) → print(True)"""
    code = generate("print(true)")
    assert code == "print(True)"

def test_codegen_print_false():
    """print(false) → print(False)"""
    code = generate("print(false)")
    assert code == "print(False)"

def test_codegen_print_string():
    """print("hello") → print("hello")"""
    code = generate('print("hello")')
    assert code == 'print("hello")'

def test_codegen_print_variable():
    """print(x) after let x = 5"""
    code = generate("let x: int = 5\nprint(x)")
    assert "print(x)" in code

def test_codegen_print_expression():
    """print(2 + 3) → print(2 + 3)"""
    code = generate("print(2 + 3)")
    assert code == "print(2 + 3)"

def test_codegen_print_function_call():
    """print(f(5)) → print(f(5))"""
    source = """fn f(n: int) -> int {
    return n
}
print(f(5))"""
    code = generate(source)
    assert "print(f(5))" in code
```

### 7.6 Integration Tests (3)

```python
# test_integration_print.py

def test_print_in_function():
    """print inside function body"""
    source = """fn greet() -> int {
    print("hello")
    return 0
}"""
    code = compile_and_run(source)
    # Should compile without error

def test_print_in_loop():
    """print inside while loop"""
    source = """let i: int = 0
while i < 3 {
    print(i)
    i = i + 1
}"""
    code = compile_and_run(source)
    # Should print: 0, 1, 2

def test_print_in_conditional():
    """print inside if/else"""
    source = """let x: int = 5
if x > 0 {
    print("positive")
} else {
    print("non-positive")
}"""
    code = compile_and_run(source)
    # Should print: positive
```

---

## 8. Impact Matrix

| Module       | Impact | Changes Required                    | Risk Level      |
| ------------ | ------ | ----------------------------------- | --------------- |
| **Lexer**    | LOW    | Add `PRINT` to keywords dict        | 🟢 Minimal       |
| **Parser**   | LOW    | Add `_parse_print_stmt()` method    | 🟢 Minimal       |
| **AST**      | LOW    | Add `PrintStmt` dataclass           | 🟢 Minimal       |
| **Semantic** | LOW    | Add `_analyze_print_stmt()` method  | 🟢 Minimal       |
| **CodeGen**  | LOW    | Add `_generate_print_stmt()` method | 🟢 Minimal       |
| **CLI**      | NONE   | No changes required                 | 🟢 None          |
| **Tests**    | MEDIUM | Add 25 new tests                    | 🟢 Additive only |

### Risk Assessment

| Risk                       | Probability | Impact | Mitigation                              |
| -------------------------- | ----------- | ------ | --------------------------------------- |
| Regression in FROZEN tests | LOW         | HIGH   | Run full test suite after each change   |
| Grammar conflicts          | LOW         | MEDIUM | `print` is unambiguous keyword          |
| AST hierarchy break        | LOW         | HIGH   | `PrintStmt` extends `Statement` cleanly |
| Semantic edge cases        | LOW         | LOW    | All primitive types are printable       |

---

## 9. Edge Cases

### 9.1 Syntactic Edge Cases

| Case                | Input              | Expected Behavior                   |
| ------------------- | ------------------ | ----------------------------------- |
| Missing parentheses | `print 42`         | Parser error                        |
| Empty print         | `print()`          | Parser error (expression required)  |
| Multiple arguments  | `print(1, 2)`      | Parser error (single arg only)      |
| Nested print        | `print(print(1))`  | Semantic error (print is statement) |
| Print as expression | `let x = print(1)` | Parser/Semantic error               |

### 9.2 Semantic Edge Cases

| Case               | Input                | Expected Behavior    |
| ------------------ | -------------------- | -------------------- |
| Undefined variable | `print(undefined)`   | Semantic error E0200 |
| Type error in expr | `print(1 + "a")`     | Semantic error E0100 |
| Print in dead code | `return 0\nprint(1)` | Warning (optional)   |

### 9.3 Runtime Edge Cases

| Case            | Input                 | Python Behavior       |
| --------------- | --------------------- | --------------------- |
| Large integer   | `print(999999999999)` | Prints correctly      |
| Float precision | `print(0.1 + 0.2)`    | `0.30000000000000004` |
| Empty string    | `print("")`           | Prints newline only   |
| Special chars   | `print("a\nb")`       | Prints with newline   |

---

## 10. Implementation Plan

### 10.1 Order of Implementation

```
Step 1: Lexer
├── Add TokenType.PRINT
├── Add "print" to KEYWORDS
└── Write 4 lexer tests

Step 2: AST
├── Create PrintStmt dataclass
└── Update AST documentation

Step 3: Parser
├── Add _parse_print_stmt()
├── Update _parse_statement()
└── Write 6 parser tests

Step 4: Semantic
├── Add _analyze_print_stmt()
├── Add error code E0400
└── Write 4 semantic tests

Step 5: CodeGen
├── Add _generate_print_stmt()
└── Write 8 codegen tests

Step 6: Integration
├── Write 3 integration tests
└── Validate all 341 tests pass (316 + 25)
```

### 10.2 Estimated Effort

| Step        | Time Estimate  | Dependencies |
| ----------- | -------------- | ------------ |
| Lexer       | 15 min         | None         |
| AST         | 10 min         | None         |
| Parser      | 20 min         | Lexer, AST   |
| Semantic    | 15 min         | AST          |
| CodeGen     | 15 min         | AST          |
| Integration | 20 min         | All above    |
| **Total**   | **~1.5 hours** |              |

---

## 11. Acceptance Criteria

### 11.1 Functional Criteria

- [ ] `print(42)` outputs `42`
- [ ] `print(3.14)` outputs `3.14`
- [ ] `print(true)` outputs `True`
- [ ] `print(false)` outputs `False`
- [ ] `print("hello")` outputs `hello`
- [ ] `print(expr)` works for any valid expression
- [ ] `print` cannot be used as identifier
- [ ] `print()` without argument is syntax error
- [ ] `print(a, b)` with multiple arguments is syntax error

### 11.2 Quality Criteria

- [ ] All 316 FROZEN tests continue passing
- [ ] All 25 new tests pass
- [ ] No changes to FROZEN phase files (only additions)
- [ ] Documentation updated
- [ ] Error messages are clear and localized

### 11.3 Sign-off Checklist

```
[ ] Phase 5 design approved
[ ] Implementation complete
[ ] 341 tests passing (316 + 25)
[ ] Code review passed
[ ] Documentation updated
[ ] Release tagged (v1.1.0)
```

---

## 12. Future Extensions (Out of Scope)

The following features are explicitly **NOT** part of Phase 5 but may be considered for future phases:

### Phase 5.1 — Multiple Arguments
```
print(a, b, c)  // Multiple values
```

### Phase 5.2 — Formatted Output
```
print("Value: {}", x)  // String interpolation
```

### Phase 5.3 — Output Control
```
print(x, end="")      // No newline
print(x, sep=", ")    // Custom separator
```

### Phase 5.4 — Additional Builtins
```
input() -> str        // Read user input
len(s: str) -> int    // String length
str(x: int) -> str    // Type conversion
```

---

## 13. Appendix

### A. Complete EBNF Grammar (Phase 5)

```ebnf
program → declaration* EOF

declaration → varDecl
            | constDecl  
            | fnDecl
            | statement

varDecl → "let" IDENTIFIER ":" type "=" expression NEWLINE

constDecl → "const" IDENTIFIER ":" type "=" expression NEWLINE

fnDecl → "fn" IDENTIFIER "(" params? ")" "->" type block

params → param ("," param)*
param → IDENTIFIER ":" type

type → "int" | "float" | "bool" | "str"

block → "{" declaration* "}"

statement → ifStmt
          | whileStmt
          | returnStmt
          | breakStmt
          | continueStmt
          | assignStmt
          | printStmt      (* NEW in Phase 5 *)
          | exprStmt

ifStmt → "if" expression block ("else" block)?
whileStmt → "while" expression block
returnStmt → "return" expression NEWLINE
breakStmt → "break" NEWLINE
continueStmt → "continue" NEWLINE
assignStmt → IDENTIFIER "=" expression NEWLINE
printStmt → "print" "(" expression ")" NEWLINE    (* NEW *)
exprStmt → expression NEWLINE

expression → orExpr
orExpr → andExpr ("||" andExpr)*
andExpr → eqExpr ("&&" eqExpr)*
eqExpr → relExpr (("==" | "!=") relExpr)*
relExpr → addExpr (("<" | ">" | "<=" | ">=") addExpr)*
addExpr → mulExpr (("+" | "-") mulExpr)*
mulExpr → unaryExpr (("*" | "/" | "%") unaryExpr)*
unaryExpr → ("!" | "-") unaryExpr | callExpr
callExpr → primary ("(" args? ")")?
args → expression ("," expression)*
primary → INT_LITERAL
        | FLOAT_LITERAL
        | STRING_LITERAL
        | "true" | "false"
        | IDENTIFIER
        | "(" expression ")"
```

### B. Error Codes Reference

| Code      | Category  | Message                                                    |
| --------- | --------- | ---------------------------------------------------------- |
| E0100     | Type      | type mismatch: expected {expected}, got {actual}           |
| E0101     | Type      | operator '{op}' not supported for types {left} and {right} |
| E0102     | Type      | unary operator '{op}' not supported for type {type}        |
| E0103     | Type      | condition must be bool, got {type}                         |
| E0200     | Scope     | undefined variable: {name}                                 |
| E0201     | Scope     | undefined function: {name}                                 |
| E0202     | Scope     | variable already declared: {name}                          |
| E0203     | Scope     | cannot reassign constant: {name}                           |
| E0300     | Control   | break outside loop                                         |
| E0301     | Control   | continue outside loop                                      |
| E0302     | Control   | missing return in function                                 |
| **E0400** | **Print** | **cannot print value of type '{type}'**                    | ← NEW |

---

## Document History

| Version | Date       | Author      | Changes       |
| ------- | ---------- | ----------- | ------------- |
| 0.1.0   | 2026-01-15 | Quasar Team | Initial draft |

---

**END OF DOCUMENT**

# Quasar Language Specification

> **Versão:** 1.8.0  
> **Status:** v1.8.0 "Pulsar" - Phase 11 Complete  
> **Última atualização:** 16 de janeiro de 2026

---

## 1. Visão Geral

**Quasar** é uma linguagem de programação estaticamente tipada, projetada para ser simples, expressiva e compilável para Python. O projeto segue uma metodologia rigorosa de fases, onde cada fase é congelada (FROZEN) antes de prosseguir para a próxima.

### 1.1 Objetivos

- Sintaxe limpa e moderna inspirada em Rust/Swift
- Sistema de tipos estático e explícito
- Transpilação para Python 3.10+
- Desenvolvimento orientado a testes (TDD)

### 1.2 Características Principais

| Característica | Descrição                                         |
| -------------- | ------------------------------------------------- |
| **Tipagem**    | Estática, explícita, sem inferência               |
| **Tipos**      | `int`, `float`, `bool`, `str`, `[T]`, `Dict[K,V]` |
| **Paradigma**  | Imperativo com funções                            |
| **Target**     | Python 3.10+                                      |
| **Extensão**   | `.qsr`                                            |

---

## 2. Decisões FROZEN por Fase

### Phase 0 — Project Definition ✅ FROZEN

- Nome da linguagem: **Quasar**
- Extensão de arquivo: `.qsr`
- Target de compilação: Python
- Metodologia: Fases sequenciais com congelamento

### Phase 1 — Grammar Design ✅ FROZEN

- Sintaxe sem ponto-e-vírgula (`;`)
- Blocos delimitados por `{ }`
- Condições sem parênteses obrigatórios
- Declaração de tipos com `:` após identificador
- Operadores lógicos: `&&`, `||`, `!`

### Phase 2 — AST Definition ✅ FROZEN

- Hierarquia: `Node` → `Expression` | `Statement` | `Declaration`
- Todos os nós possuem `Span` para rastreamento de posição
- Tipos representados por `TypeAnnotation` enum

### Phase 3 — Semantic Analysis ✅ FROZEN

- Sistema de tipos fechado (4 tipos primitivos)
- **Ausência de tipo `void`/`unit`** — todas as funções retornam valor
- Sem coerção implícita entre tipos
- Escopos aninhados com shadowing permitido

### Phase 4 — Code Generation ✅ FROZEN

- Transpilação AST → Python
- Testes criados e passando
- Implementação completa

### Phase 5 — Print Statement ✅ FROZEN

- `print()` builtin com múltiplos argumentos
- Parâmetros `sep` e `end`
- String interpolation com `{}`

### Phase 6 — Lists & Ranges ✅ FROZEN

- Tipo `[T]` para listas
- Sintaxe de range `0..10`
- Loops `for i in range`

### Phase 7 — I/O & Casting ✅ FROZEN

- `input()` builtin
- Casting: `int()`, `float()`, `str()`, `bool()`

### Phase 8 — Structs ✅ FROZEN

- Declaração: `struct Point { x: int, y: int }`
- Instanciação e acesso a membros

### Phase 9 — Modules & Imports ✅ FROZEN

- `import math` (Python stdlib)
- `import "./file.qsr"` (local files)

### Phase 10 — Dictionaries ✅ FROZEN

- Tipo `Dict[K, V]`
- Literais, indexação, builtins

### Phase 11 — Primitive Methods ✅ FROZEN

- Métodos nativos para str, list, dict
- 23 métodos implementados
- Generic type resolution

---

## 3. Gramática e Sintaxe

### 3.1 Programa

```ebnf
program        → declaration* EOF

declaration    → varDecl
               | constDecl
               | fnDecl
               | statement

statement      → exprStmt
               | ifStmt
               | whileStmt
               | returnStmt
               | breakStmt
               | continueStmt
               | assignStmt
               | block
```

### 3.2 Declarações

```ebnf
varDecl        → "let" IDENTIFIER ":" type "=" expression
constDecl      → "const" IDENTIFIER ":" type "=" expression
fnDecl         → "fn" IDENTIFIER "(" parameters? ")" "->" type block

parameters     → param ("," param)*
param          → IDENTIFIER ":" type

type           → "int" | "float" | "bool" | "str"
```

### 3.3 Statements

```ebnf
block          → "{" declaration* "}"

ifStmt         → "if" expression block ("else" block)?
whileStmt      → "while" expression block

returnStmt     → "return" expression
breakStmt      → "break"
continueStmt   → "continue"

assignStmt     → IDENTIFIER "=" expression
exprStmt       → expression
```

### 3.4 Expressões

```ebnf
expression     → logicOr

logicOr        → logicAnd ("||" logicAnd)*
logicAnd       → equality ("&&" equality)*
equality       → comparison (("==" | "!=") comparison)*
comparison     → term (("<" | ">" | "<=" | ">=") term)*
term           → factor (("+" | "-") factor)*
factor         → unary (("*" | "/" | "%") unary)*
unary          → ("!" | "-") unary | call
call           → primary ("(" arguments? ")")*
primary        → IDENTIFIER | NUMBER | STRING | "true" | "false" | "(" expression ")"

arguments      → expression ("," expression)*
```

### 3.5 Exemplos de Sintaxe

```quasar
// Variáveis e constantes
let x: int = 42
const PI: float = 3.14159
let name: str = "Quasar"
let active: bool = true

// Funções (SEMPRE com tipo de retorno)
fn add(a: int, b: int) -> int {
    return a + b
}

fn isPositive(n: int) -> bool {
    if n > 0 {
        return true
    }
    return false
}

// Loops
fn countdown(n: int) -> int {
    let i: int = n
    while i > 0 {
        i = i - 1
    }
    return i
}

// Operadores lógicos
let result: bool = true && false || !true
```

---

## 4. Estrutura do AST

### 4.1 Hierarquia de Nós

```
Node (abstract)
├── Expression (abstract)
│   ├── BinaryExpr      (left, operator, right)
│   ├── UnaryExpr       (operator, operand)
│   ├── CallExpr        (callee, arguments)
│   ├── MethodCallExpr  (object, method, arguments)  # v1.8.0
│   ├── MemberAccessExpr(object, member)             # v1.5.0
│   ├── IndexExpr       (object, index)              # v1.2.0
│   ├── Identifier      (name)
│   ├── IntLiteral      (value)
│   ├── FloatLiteral    (value)
│   ├── StringLiteral   (value)
│   ├── BoolLiteral     (value)
│   ├── ListLiteral     (elements)                   # v1.2.0
│   ├── DictLiteral     (pairs)                      # v1.7.0
│   └── RangeExpr       (start, end)                 # v1.2.0
│
├── Statement (abstract)
│   ├── Block           (declarations)
│   ├── ExpressionStmt  (expression)
│   ├── PrintStmt       (arguments, sep, end, fmt)   # v1.1.0
│   ├── IfStmt          (condition, then_block, else_block?)
│   ├── WhileStmt       (condition, body)
│   ├── ForStmt         (variable, iterable, body)   # v1.2.0
│   ├── ReturnStmt      (value)
│   ├── BreakStmt
│   ├── ContinueStmt
│   └── AssignStmt      (target, value)
│
├── Declaration (abstract)
│   ├── VarDecl         (name, type_annotation, initializer)
│   ├── ConstDecl       (name, type_annotation, initializer)
│   ├── FnDecl          (name, params, return_type, body)
│   ├── StructDecl      (name, fields)               # v1.5.0
│   ├── ImportDecl      (module, path)               # v1.6.0
│   └── Param           (name, type_annotation)
│
└── Program             (declarations)
```

### 4.2 Tipos e Operadores

```python
class TypeAnnotation(Enum):
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    STR = auto()

class BinaryOp(Enum):
    # Arithmetic
    ADD = auto()    # +
    SUB = auto()    # -
    MUL = auto()    # *
    DIV = auto()    # /
    MOD = auto()    # %
    # Comparison
    EQ = auto()     # ==
    NE = auto()     # !=
    LT = auto()     # <
    GT = auto()     # >
    LE = auto()     # <=
    GE = auto()     # >=
    # Logical
    AND = auto()    # &&
    OR = auto()     # ||

class UnaryOp(Enum):
    NEG = auto()    # -
    NOT = auto()    # !
```

### 4.3 Span (Localização)

```python
@dataclass
class Span:
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    filename: str = "<stdin>"
```

---

## 5. Regras Semânticas

### 5.1 Sistema de Tipos

| Tipo         | Descrição       | Literais         |
| ------------ | --------------- | ---------------- |
| `int`        | Inteiro         | `42`, `0`, `-1`  |
| `float`      | Ponto flutuante | `3.14`, `0.0`    |
| `bool`       | Booleano        | `true`, `false`  |
| `str`        | String          | `"hello"`        |
| `[T]`        | Lista           | `[1, 2, 3]`      |
| `Dict[K, V]` | Dicionário      | `{ "a": 1 }`     |
| `StructName` | Struct definida | `Point { x: 0 }` |

**Decisão FROZEN:** O sistema de tipos é **fechado**. Não há tipo `void`/`unit`.

### 5.2 Regras de Escopo

| Código | Erro             | Descrição                          |
| ------ | ---------------- | ---------------------------------- |
| E0001  | Undeclared       | Uso de identificador não declarado |
| E0002  | Redeclaration    | Redeclaração no mesmo escopo       |
| E0003  | Const Assignment | Atribuição a constante             |

- **Shadowing**: Permitido em escopos internos
- **Lookup**: Busca do escopo atual para o global

### 5.3 Regras de Tipos

| Código | Erro               | Descrição                                  |
| ------ | ------------------ | ------------------------------------------ |
| E0100  | Type Mismatch      | Tipo incompatível em declaração/atribuição |
| E0101  | Non-Bool Condition | Condição de `if`/`while` não é `bool`      |
| E0102  | Invalid Operands   | Operandos incompatíveis para operador      |
| E0103  | String Comparison  | Comparação `<`/`>`/`<=`/`>=` com strings   |
| E0104  | Logical Type       | Operador lógico com não-booleano           |

**Regras de operadores:**

```
Arithmetic (+, -, *, /, %):
  - int OP int → int
  - float OP float → float
  - str + str → str (apenas concatenação)
  - PROIBIDO: int OP float (sem coerção)

Comparison (==, !=):
  - T == T → bool (mesmo tipo)

Comparison (<, >, <=, >=):
  - int OP int → bool
  - float OP float → bool
  - PROIBIDO: strings

Logical (&&, ||):
  - bool OP bool → bool

Unary (!):
  - !bool → bool

Unary (-):
  - -int → int
  - -float → float
```

### 5.4 Regras de Fluxo de Controle

| Código | Erro                  | Descrição                                |
| ------ | --------------------- | ---------------------------------------- |
| E0200  | Break Outside Loop    | `break` fora de loop                     |
| E0201  | Continue Outside Loop | `continue` fora de loop                  |
| E0302  | Return Type Mismatch  | Tipo de retorno não corresponde à função |

**Decisão FROZEN:** 
- Todas as funções DEVEM ter tipo de retorno declarado
- Todas as funções DEVEM retornar um valor
- Não existe `return` sem expressão

---

## 6. Pipeline do Compilador

```
┌─────────────────────────────────────────────────────────────┐
│                      QUASAR COMPILER                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Source (.qsr)                                             │
│        │                                                    │
│        ▼                                                    │
│   ┌─────────┐                                               │
│   │  Lexer  │  → Tokens                                     │
│   └────┬────┘                                               │
│        │                                                    │
│        ▼                                                    │
│   ┌─────────┐                                               │
│   │ Parser  │  → AST                                        │
│   └────┬────┘                                               │
│        │                                                    │
│        ▼                                                    │
│   ┌──────────────────┐                                      │
│   │ Semantic Analyzer │  → Validated AST                    │
│   └────────┬─────────┘                                      │
│            │                                                │
│            ▼                                                │
│   ┌────────────────┐                                        │
│   │ Code Generator │  → Python Source                       │
│   └────────────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.1 Componentes

| Componente | Módulo            | Responsabilidade         |
| ---------- | ----------------- | ------------------------ |
| Lexer      | `quasar.lexer`    | Tokenização              |
| Parser     | `quasar.parser`   | Análise sintática → AST  |
| Semantic   | `quasar.semantic` | Validação semântica      |
| CodeGen    | `quasar.codegen`  | Geração de código Python |

### 6.2 Estrutura de Diretórios

```
src/quasar/
├── __init__.py
├── ast/
│   ├── __init__.py
│   ├── base.py          # Node, Expression, Statement, Declaration
│   ├── declarations.py  # VarDecl, ConstDecl, FnDecl, Param
│   ├── expressions.py   # BinaryExpr, UnaryExpr, CallExpr, literals
│   ├── operators.py     # BinaryOp, UnaryOp
│   ├── program.py       # Program
│   ├── span.py          # Span
│   ├── statements.py    # Block, IfStmt, WhileStmt, etc.
│   └── types.py         # TypeAnnotation
├── lexer/
│   ├── __init__.py
│   ├── errors.py        # LexerError
│   ├── lexer.py         # Lexer
│   └── tokens.py        # Token, TokenType
├── parser/
│   ├── __init__.py
│   ├── errors.py        # ParserError
│   └── parser.py        # Parser
├── semantic/
│   ├── __init__.py
│   ├── analyzer.py      # SemanticAnalyzer
│   ├── errors.py        # SemanticError
│   └── symbols.py       # Symbol, SymbolTable
└── codegen/
    ├── __init__.py
    └── generator.py     # CodeGenerator (stub)
```

---

## 7. Status das Fases

| Fase                         | Status   | Testes | Observação             |
| ---------------------------- | -------- | ------ | ---------------------- |
| Phase 0 — Project Definition | ✅ FROZEN | —      | Definições base        |
| Phase 1 — Grammar Design     | ✅ FROZEN | —      | Sintaxe sem `;`        |
| Phase 2 — AST Definition     | ✅ FROZEN | —      | Hierarquia completa    |
| Lexer Implementation         | ✅ FROZEN | 103    | Tokenização            |
| Parser Implementation        | ✅ FROZEN | 105    | AST generation         |
| Phase 3 — Semantic Analysis  | ✅ FROZEN | 100    | Validação completa     |
| Phase 4 — Code Generation    | ✅ FROZEN | 118    | Python emission        |
| Phase 5 — Print Statement    | ✅ FROZEN | 90     | E2E tests              |
| Phase 6 — Lists & Ranges     | ✅ FROZEN | 159    | list, range, for       |
| Phase 7 — I/O & Casting      | ✅ FROZEN | 66     | input, int/float/str   |
| Phase 8 — Structs            | ✅ FROZEN | 46     | User-defined types     |
| Phase 9 — Modules & Imports  | ✅ FROZEN | 31     | Python + local imports |
| Phase 10 — Dictionaries      | ✅ FROZEN | 86     | Dict[K, V]             |
| Phase 11 — Primitive Methods | ✅ FROZEN | 81     | Native methods         |

**Total de testes:** 1022

---

## 8. Status Atual

### 8.1 Versão Atual

**Versão:** v1.8.0 "Pulsar" — Phase 11 Complete ✅

Todas as fases principais estão implementadas e FROZEN. O compilador está funcional com:
- 1022 testes passando
- 23 métodos nativos para tipos primitivos
- Suporte completo a módulos, structs, listas e dicionários

### 8.2 Mapeamento Quasar → Python

| Quasar                        | Python                   |
| ----------------------------- | ------------------------ |
| `let x: int = 1`              | `x = 1`                  |
| `const PI: float = 3.14`      | `PI = 3.14`              |
| `fn f(a: int) -> int { ... }` | `def f(a):\n    ...`     |
| `if cond { ... }`             | `if cond:\n    ...`      |
| `while cond { ... }`          | `while cond:\n    ...`   |
| `for i in 0..10 { ... }`      | `for i in range(0, 10):` |
| `s.trim()`                    | `s.strip()`              |
| `l.push(v)`                   | `l.append(v)`            |
| `d.has_key(k)`                | `(k in d)`               |
| `true` / `false`              | `True` / `False`         |
| `&&` / `\|\|` / `!`           | `and` / `or` / `not`     |

---

## Apêndice A: Exemplos Completos

### A.1 Programa Simples

```quasar
// fibonacci.qsr
fn fib(n: int) -> int {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

let result: int = fib(10)
```

**Python gerado (esperado):**

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

result = fib(10)
```

### A.2 Programa com Loop

```quasar
// countdown.qsr
fn countdown(start: int) -> int {
    let i: int = start
    while i > 0 {
        i = i - 1
    }
    return i
}

const LIMIT: int = 100
let final: int = countdown(LIMIT)
```

**Python gerado (esperado):**

```python
def countdown(start):
    i = start
    while i > 0:
        i = i - 1
    return i

LIMIT = 100
final = countdown(LIMIT)
```

---

## Apêndice B: Códigos de Erro

| Código | Categoria | Mensagem                                                     |
| ------ | --------- | ------------------------------------------------------------ |
| E0001  | Scope     | use of undeclared identifier '{name}'                        |
| E0002  | Scope     | redeclaration of '{name}' in the same scope                  |
| E0003  | Scope     | cannot assign to constant '{name}'                           |
| E0100  | Type      | type mismatch: expected {expected}, got {actual}             |
| E0101  | Type      | condition must be bool, got {type}                           |
| E0102  | Type      | cannot {operation} {type1} with {type2}                      |
| E0103  | Type      | string comparison with '<', '>', '<=', '>=' is not supported |
| E0104  | Type      | logical operator requires bool operands, got {type}          |
| E0200  | Control   | 'break' outside of loop                                      |
| E0201  | Control   | 'continue' outside of loop                                   |
| E0302  | Control   | return type mismatch: expected {expected}, got {actual}      |
| E1100  | Method    | generic type mismatch in method call                         |
| E1102  | Method    | join() only valid on [str] lists                             |
| E1105  | Method    | unknown method '{method}' on type '{type}'                   |
| E1106  | Method    | method '{method}' expects {n} arguments, got {m}             |
| E1107  | Method    | method argument type mismatch                                |

---

*Documento gerado automaticamente. Qualquer alteração deve passar por revisão formal.*

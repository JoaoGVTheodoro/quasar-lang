# Quasar

**Quasar** is a programming language that compiles to Python.

**Status:** Phase 2 — AST Definition (Frozen)

## Overview

- **Extension:** `.qsr`
- **Target:** Python 3.10+
- **Paradigm:** Imperative, procedural
- **Type system:** Static, explicit, closed

## Philosophy

- Explicit semantics — no implicit behavior
- Zero magic — no automatic coercions
- Predictability — same input, same behavior
- Clarity over brevity

## Project Structure

```
quasar/
├── src/quasar/       # Compiler source code
│   ├── lexer/        # Lexical analysis
│   ├── parser/       # Syntactic analysis
│   ├── ast/          # Abstract Syntax Tree
│   ├── semantic/     # Semantic analysis
│   ├── codegen/      # Code generation (Python)
│   └── cli/          # Command-line interface
├── tests/            # Test suite
├── examples/         # Example .qsr files
└── docs/spec/        # Language specification
```

## Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT

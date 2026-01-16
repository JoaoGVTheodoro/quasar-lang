"""
Tests for code generation of declarations.

Covers: VarDecl, ConstDecl, FnDecl

Note: Quasar grammar does NOT use semicolons as statement terminators.
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.codegen import CodeGenerator


def generate(source: str) -> str:
    """Helper to parse and generate code from Quasar source."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    code = CodeGenerator().generate(ast)
    # Strip Phase 13 imports for legacy tests
    code = code.replace("import os as _q_os\nimport sys as _q_sys\n\n", "")
    return code


class TestVarDecl:
    """Tests for variable declaration generation."""
    
    def test_int_var(self):
        source = "let x: int = 1"
        result = generate(source)
        assert result == "x = 1"
    
    def test_float_var(self):
        source = "let pi: float = 3.14"
        result = generate(source)
        assert result == "pi = 3.14"
    
    def test_bool_var(self):
        source = "let flag: bool = true"
        result = generate(source)
        assert result == "flag = True"
    
    def test_str_var(self):
        source = 'let name: str = "quasar"'
        result = generate(source)
        assert result == 'name = "quasar"'


class TestConstDecl:
    """Tests for constant declaration generation."""
    
    def test_const_int(self):
        source = "const MAX: int = 100"
        result = generate(source)
        assert result == "MAX = 100"
    
    def test_const_float(self):
        source = "const PI: float = 3.14159"
        result = generate(source)
        assert result == "PI = 3.14159"
    
    def test_const_str(self):
        source = 'const GREETING: str = "hello"'
        result = generate(source)
        assert result == 'GREETING = "hello"'


class TestFnDecl:
    """Tests for function declaration generation."""
    
    def test_fn_no_params(self):
        source = "fn answer() -> int { return 42 }"
        result = generate(source)
        expected = "def answer():\n    return 42"
        assert result == expected
    
    def test_fn_one_param(self):
        source = "fn double(x: int) -> int { return x }"
        result = generate(source)
        expected = "def double(x):\n    return x"
        assert result == expected
    
    def test_fn_multiple_params(self):
        source = "fn add(a: int, b: int) -> int { return a }"
        result = generate(source)
        expected = "def add(a, b):\n    return a"
        assert result == expected
    
    def test_fn_with_local_var(self):
        source = """
        fn compute(x: int) -> int {
            let y: int = 10
            return y
        }
        """
        result = generate(source)
        expected = "def compute(x):\n    y = 10\n    return y"
        assert result == expected
    
    def test_fn_with_multiple_statements(self):
        source = """
        fn process(n: int) -> int {
            let a: int = 1
            let b: int = 2
            return a
        }
        """
        result = generate(source)
        expected = "def process(n):\n    a = 1\n    b = 2\n    return a"
        assert result == expected

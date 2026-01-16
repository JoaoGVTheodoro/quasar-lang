"""
Tests for code generation of literals.

Covers: IntLiteral, FloatLiteral, StringLiteral, BoolLiteral

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


class TestIntLiteral:
    """Tests for integer literal generation."""
    
    def test_simple_int(self):
        source = "let x: int = 42"
        result = generate(source)
        assert result == "x = 42"
    
    def test_zero(self):
        source = "let x: int = 0"
        result = generate(source)
        assert result == "x = 0"
    
    def test_large_int(self):
        source = "let x: int = 999999"
        result = generate(source)
        assert result == "x = 999999"


class TestFloatLiteral:
    """Tests for float literal generation."""
    
    def test_simple_float(self):
        source = "let x: float = 3.14"
        result = generate(source)
        assert result == "x = 3.14"
    
    def test_float_zero(self):
        source = "let x: float = 0.0"
        result = generate(source)
        assert result == "x = 0.0"


class TestStringLiteral:
    """Tests for string literal generation."""
    
    def test_simple_string(self):
        source = 'let x: str = "hello"'
        result = generate(source)
        assert result == 'x = "hello"'
    
    def test_empty_string(self):
        source = 'let x: str = ""'
        result = generate(source)
        assert result == 'x = ""'


class TestBoolLiteral:
    """Tests for boolean literal generation."""
    
    def test_true(self):
        source = "let x: bool = true"
        result = generate(source)
        assert result == "x = True"
    
    def test_false(self):
        source = "let x: bool = false"
        result = generate(source)
        assert result == "x = False"

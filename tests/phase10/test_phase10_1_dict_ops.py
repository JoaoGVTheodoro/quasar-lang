"""
Phase 10.1 — Dictionary Operations Tests.

Tests for dictionary read (`d[key]`) and write (`d[key] = value`) operations.

Test coverage:
- Read valid: d["key"] where d is Dict[str, int]
- Write valid: d["key"] = 123
- New key insertion: d["new"] = 456
- Nested access: d["key"].field
- Error E1003: Wrong key type (e.g., d[1] on Dict[str, int])
- Error E1004: Wrong value type (e.g., d["k"] = "text" on Dict[str, int])
- Runtime KeyError: Reading non-existent key
"""

import pytest
import subprocess
import sys
import tempfile
import os

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator


def compile_to_python(source: str) -> str:
    """Helper to compile Quasar source to Python."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    generator = CodeGenerator()
    return generator.generate(ast)


def analyze_only(source: str):
    """Helper to parse and analyze source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return ast


def run_python(code: str) -> str:
    """Helper to run generated Python code and return output."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        try:
            result = subprocess.run(
                [sys.executable, f.name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        finally:
            os.unlink(f.name)


# =============================================================================
# Read Operations (Valid Cases)
# =============================================================================


class TestDictReadValid:
    """Tests for valid dictionary read operations."""

    def test_read_str_key_int_value(self):
        """Read Dict[str, int] with string key returns int."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
let x: int = d["a"]
print(x)
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "1"

    def test_read_int_key_str_value(self):
        """Read Dict[int, str] with int key returns str."""
        source = '''
let d: Dict[int, str] = {1: "one", 2: "two"}
let x: str = d[1]
print(x)
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "one"

    def test_read_bool_key(self):
        """Read Dict[bool, int] with bool key."""
        source = '''
let d: Dict[bool, int] = {true: 100, false: 0}
let x: int = d[true]
print(x)
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "100"

    def test_read_with_expression_key(self):
        """Read dict with expression as key."""
        source = '''
let d: Dict[int, str] = {10: "ten", 20: "twenty"}
let k: int = 10
let x: str = d[k]
print(x)
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "ten"


# =============================================================================
# Write Operations (Valid Cases)
# =============================================================================


class TestDictWriteValid:
    """Tests for valid dictionary write operations."""

    def test_write_existing_key(self):
        """Update existing key in dict."""
        source = '''
let d: Dict[str, int] = {"a": 1}
d["a"] = 100
print(d["a"])
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "100"

    def test_write_new_key(self):
        """Insert new key into dict."""
        source = '''
let d: Dict[str, int] = {"a": 1}
d["b"] = 2
print(d["b"])
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "2"

    def test_write_int_key(self):
        """Write with int key."""
        source = '''
let d: Dict[int, str] = {1: "one"}
d[2] = "two"
print(d[2])
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "two"

    def test_write_with_expression_value(self):
        """Write with computed value."""
        source = '''
let d: Dict[str, int] = {}
let x: int = 40
d["key"] = x + 2
print(d["key"])
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "42"


# =============================================================================
# Semantic Errors
# =============================================================================


class TestDictSemanticErrors:
    """Tests for semantic errors in dict operations."""

    def test_error_e1003_wrong_key_type_read(self):
        """E1003: Reading dict with wrong key type."""
        source = '''
let d: Dict[str, int] = {"a": 1}
let x: int = d[1]
'''
        with pytest.raises(Exception) as exc_info:
            analyze_only(source)
        assert "E1003" in str(exc_info.value)
        assert "key type mismatch" in str(exc_info.value)

    def test_error_e1003_wrong_key_type_write(self):
        """E1003: Writing dict with wrong key type."""
        source = '''
let d: Dict[str, int] = {"a": 1}
d[123] = 100
'''
        with pytest.raises(Exception) as exc_info:
            analyze_only(source)
        assert "E1003" in str(exc_info.value)

    def test_error_e1004_wrong_value_type(self):
        """E1004: Writing dict with wrong value type."""
        source = '''
let d: Dict[str, int] = {"a": 1}
d["b"] = "text"
'''
        with pytest.raises(Exception) as exc_info:
            analyze_only(source)
        assert "E1004" in str(exc_info.value)
        assert "value type mismatch" in str(exc_info.value)

    def test_error_e1004_wrong_value_type_bool_to_int(self):
        """E1004: Cannot assign bool to int dict."""
        source = '''
let d: Dict[str, int] = {}
d["flag"] = true
'''
        with pytest.raises(Exception) as exc_info:
            analyze_only(source)
        assert "E1004" in str(exc_info.value)


# =============================================================================
# Code Generation
# =============================================================================


class TestDictCodeGen:
    """Tests for dict operation code generation."""

    def test_codegen_read(self):
        """Dict read generates proper Python code."""
        source = '''
let d: Dict[str, int] = {"a": 1}
let x: int = d["a"]
'''
        code = compile_to_python(source)
        assert 'd["a"]' in code

    def test_codegen_write(self):
        """Dict write generates proper Python code."""
        source = '''
let d: Dict[str, int] = {}
d["key"] = 42
'''
        code = compile_to_python(source)
        assert 'd["key"] = 42' in code


# =============================================================================
# Runtime Behavior
# =============================================================================


class TestDictRuntime:
    """Tests for runtime behavior of dict operations."""

    def test_runtime_keyerror(self):
        """Reading non-existent key raises KeyError at runtime."""
        source = '''
let d: Dict[str, int] = {"a": 1}
print(d["nonexistent"])
'''
        code = compile_to_python(source)
        # Run and expect KeyError
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            try:
                result = subprocess.run(
                    [sys.executable, f.name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                assert result.returncode != 0
                assert "KeyError" in result.stderr
            finally:
                os.unlink(f.name)

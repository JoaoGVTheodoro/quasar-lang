"""
Phase 10.2 — Dictionary Built-ins Tests.

Tests for dictionary built-in functions: len(), keys(), values().

Test coverage:
- len(dict): Returns number of entries
- keys(dict): Returns list of keys
- values(dict): Returns list of values
- Empty dict: keys({}) and values({}) return empty list
- Type errors: keys() and values() require dict argument
- Integration: Indexing into keys/values result
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
# len() Built-in
# =============================================================================


class TestDictLen:
    """Tests for len() on dictionaries."""

    def test_len_dict_nonempty(self):
        """len() returns correct count for non-empty dict."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2, "c": 3}
print(len(d))
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "3"

    def test_len_dict_empty(self):
        """len() returns 0 for empty dict."""
        source = '''
let d: Dict[str, int] = {}
print(len(d))
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "0"

    def test_len_dict_int_keys(self):
        """len() works with int-keyed dict."""
        source = '''
let d: Dict[int, str] = {1: "one", 2: "two"}
print(len(d))
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "2"


# =============================================================================
# keys() Built-in
# =============================================================================


class TestDictKeys:
    """Tests for keys() built-in function."""

    def test_keys_returns_list(self):
        """keys() returns a list of keys."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
let k: [str] = keys(d)
print(len(k))
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "2"

    def test_keys_empty_dict(self):
        """keys() on empty dict returns empty list."""
        source = '''
let d: Dict[str, int] = {}
let k: [str] = keys(d)
print(len(k))
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "0"

    def test_keys_index_access(self):
        """Can index into keys() result."""
        source = '''
let d: Dict[int, str] = {10: "ten", 20: "twenty"}
let k: [int] = keys(d)
let first: int = k[0]
print(first)
'''
        code = compile_to_python(source)
        output = run_python(code)
        # Order may vary, but should be 10 or 20
        assert output in ("10", "20")

    def test_keys_error_not_dict(self):
        """E1005: keys() requires dict argument."""
        source = '''
let s: str = "hello"
let k: [str] = keys(s)
'''
        with pytest.raises(Exception) as exc_info:
            analyze_only(source)
        assert "E1005" in str(exc_info.value)
        assert "must be a dict" in str(exc_info.value)


# =============================================================================
# values() Built-in
# =============================================================================


class TestDictValues:
    """Tests for values() built-in function."""

    def test_values_returns_list(self):
        """values() returns a list of values."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
let v: [int] = values(d)
print(len(v))
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "2"

    def test_values_empty_dict(self):
        """values() on empty dict returns empty list."""
        source = '''
let d: Dict[str, int] = {}
let v: [int] = values(d)
print(len(v))
'''
        code = compile_to_python(source)
        output = run_python(code)
        assert output == "0"

    def test_values_index_access(self):
        """Can index into values() result."""
        source = '''
let d: Dict[str, int] = {"x": 100, "y": 200}
let v: [int] = values(d)
let first: int = v[0]
print(first)
'''
        code = compile_to_python(source)
        output = run_python(code)
        # Order may vary
        assert output in ("100", "200")

    def test_values_error_not_dict(self):
        """E1006: values() requires dict argument."""
        source = '''
let n: int = 123
let v: [int] = values(n)
'''
        with pytest.raises(Exception) as exc_info:
            analyze_only(source)
        assert "E1006" in str(exc_info.value)
        assert "must be a dict" in str(exc_info.value)


# =============================================================================
# Code Generation
# =============================================================================


class TestDictBuiltinsCodeGen:
    """Tests for dict built-in code generation."""

    def test_codegen_keys(self):
        """keys() generates list(d.keys())."""
        source = '''
let d: Dict[str, int] = {"a": 1}
let k: [str] = keys(d)
'''
        code = compile_to_python(source)
        assert "list(d.keys())" in code

    def test_codegen_values(self):
        """values() generates list(d.values())."""
        source = '''
let d: Dict[str, int] = {"a": 1}
let v: [int] = values(d)
'''
        code = compile_to_python(source)
        assert "list(d.values())" in code

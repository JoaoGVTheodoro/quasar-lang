"""
Phase 11.1 — String Methods Tests.

Tests for string manipulation, verification, and conversion methods.

Test coverage:
- Manipulation: upper, lower, trim, replace, split
- Verification: contains, starts_with, ends_with
- Conversion: to_int, to_float
- Error handling: E1105, E1106
- Method chaining
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.semantic.errors import SemanticError
from quasar.codegen import CodeGenerator
from quasar.ast import ListType, STR


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


def execute_and_capture(source: str) -> str:
    """Compile, execute, and capture stdout."""
    code = compile_to_python(source)
    import io
    import sys
    captured = io.StringIO()
    sys.stdout = captured
    try:
        exec(code)
    finally:
        sys.stdout = sys.__stdout__
    return captured.getvalue().strip()


# =============================================================================
# Manipulation Methods
# =============================================================================


class TestStringManipulation:
    """Tests for string manipulation methods."""

    def test_upper(self):
        """upper() converts to uppercase."""
        source = '''
let s: str = "hello"
print(s.upper())
'''
        result = execute_and_capture(source)
        assert result == "HELLO"

    def test_upper_mixed_case(self):
        """upper() handles mixed case."""
        source = '''
let s: str = "HeLLo WoRLd"
print(s.upper())
'''
        result = execute_and_capture(source)
        assert result == "HELLO WORLD"

    def test_lower(self):
        """lower() converts to lowercase."""
        source = '''
let s: str = "HELLO"
print(s.lower())
'''
        result = execute_and_capture(source)
        assert result == "hello"

    def test_trim(self):
        """trim() removes leading and trailing whitespace."""
        source = '''
let s: str = "  hello world  "
print(s.trim())
'''
        result = execute_and_capture(source)
        assert result == "hello world"

    def test_trim_tabs_and_newlines(self):
        """trim() removes tabs and newlines too."""
        source = r'''
let s: str = "\t\nhello\n\t"
print(s.trim())
'''
        # Note: The literal \t and \n in source are escape sequences
        code = compile_to_python(source)
        assert '.strip()' in code

    def test_replace(self):
        """replace() substitutes substrings."""
        source = '''
let s: str = "hello"
print(s.replace("l", "x"))
'''
        result = execute_and_capture(source)
        assert result == "hexxo"

    def test_replace_word(self):
        """replace() can substitute whole words."""
        source = '''
let s: str = "hello world"
print(s.replace("world", "quasar"))
'''
        result = execute_and_capture(source)
        assert result == "hello quasar"

    def test_split(self):
        """split() returns a list of strings."""
        source = '''
let s: str = "a,b,c"
let parts: [str] = s.split(",")
print(parts[0])
print(parts[1])
print(parts[2])
'''
        result = execute_and_capture(source)
        assert result == "a\nb\nc"

    def test_split_space(self):
        """split() with space separator."""
        source = '''
let s: str = "hello world quasar"
let words: [str] = s.split(" ")
print(words.len())
'''
        result = execute_and_capture(source)
        assert result == "3"


# =============================================================================
# Verification Methods
# =============================================================================


class TestStringVerification:
    """Tests for string verification methods."""

    def test_contains_true(self):
        """contains() returns true when substring exists."""
        source = '''
let s: str = "hello world"
print(s.contains("world"))
'''
        result = execute_and_capture(source)
        assert result == "True"

    def test_contains_false(self):
        """contains() returns false when substring doesn't exist."""
        source = '''
let s: str = "hello world"
print(s.contains("quasar"))
'''
        result = execute_and_capture(source)
        assert result == "False"

    def test_starts_with_true(self):
        """starts_with() returns true for matching prefix."""
        source = '''
let s: str = "hello world"
print(s.starts_with("hello"))
'''
        result = execute_and_capture(source)
        assert result == "True"

    def test_starts_with_false(self):
        """starts_with() returns false for non-matching prefix."""
        source = '''
let s: str = "hello world"
print(s.starts_with("world"))
'''
        result = execute_and_capture(source)
        assert result == "False"

    def test_ends_with_true(self):
        """ends_with() returns true for matching suffix."""
        source = '''
let filename: str = "document.txt"
print(filename.ends_with(".txt"))
'''
        result = execute_and_capture(source)
        assert result == "True"

    def test_ends_with_false(self):
        """ends_with() returns false for non-matching suffix."""
        source = '''
let filename: str = "document.txt"
print(filename.ends_with(".pdf"))
'''
        result = execute_and_capture(source)
        assert result == "False"


# =============================================================================
# Conversion Methods
# =============================================================================


class TestStringConversion:
    """Tests for string to number conversion methods."""

    def test_to_int(self):
        """to_int() converts string to integer."""
        source = '''
let s: str = "42"
let n: int = s.to_int()
print(n + 8)
'''
        result = execute_and_capture(source)
        assert result == "50"

    def test_to_int_negative(self):
        """to_int() handles negative numbers."""
        source = '''
let s: str = "-123"
print(s.to_int())
'''
        result = execute_and_capture(source)
        assert result == "-123"

    def test_to_float(self):
        """to_float() converts string to float."""
        source = '''
let s: str = "3.14"
let f: float = s.to_float()
print(f)
'''
        result = execute_and_capture(source)
        assert result == "3.14"

    def test_to_float_integer_string(self):
        """to_float() can convert integer strings."""
        source = '''
let s: str = "42"
let f: float = s.to_float()
print(f)
'''
        result = execute_and_capture(source)
        assert result == "42.0"


# =============================================================================
# Code Generation Tests
# =============================================================================


class TestCodeGen:
    """Tests for correct Python code generation."""

    def test_codegen_trim_to_strip(self):
        """trim() generates .strip()."""
        source = '''
let s: str = " x "
let t: str = s.trim()
'''
        code = compile_to_python(source)
        assert 't = s.strip()' in code

    def test_codegen_contains_to_in(self):
        """contains() generates 'in' operator."""
        source = '''
let s: str = "hello"
let b: bool = s.contains("ell")
'''
        code = compile_to_python(source)
        assert 'b = ("ell" in s)' in code

    def test_codegen_to_int(self):
        """to_int() generates int()."""
        source = '''
let s: str = "42"
let n: int = s.to_int()
'''
        code = compile_to_python(source)
        assert 'n = int(s)' in code

    def test_codegen_starts_with(self):
        """starts_with() generates .startswith()."""
        source = '''
let s: str = "hello"
let b: bool = s.starts_with("he")
'''
        code = compile_to_python(source)
        assert 'b = s.startswith("he")' in code

    def test_codegen_ends_with(self):
        """ends_with() generates .endswith()."""
        source = '''
let s: str = "hello"
let b: bool = s.ends_with("lo")
'''
        code = compile_to_python(source)
        assert 'b = s.endswith("lo")' in code


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrors:
    """Tests for error detection."""

    def test_error_e1105_invalid_method(self):
        """E1105: String has no push method."""
        source = '''
let s: str = "hello"
s.push("x")
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1105"
        assert "no method 'push'" in excinfo.value.message

    def test_error_e1106_split_no_args(self):
        """E1106: split requires 1 argument."""
        source = '''
let s: str = "a,b,c"
let parts: [str] = s.split()
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1106"
        assert "expects 1 argument(s), got 0" in excinfo.value.message

    def test_error_e1106_upper_with_args(self):
        """E1106: upper takes no arguments."""
        source = '''
let s: str = "hello"
let u: str = s.upper("x")
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1106"
        assert "expects 0 argument(s), got 1" in excinfo.value.message

    def test_error_e1107_wrong_arg_type(self):
        """E1107: Argument type mismatch."""
        source = '''
let s: str = "hello"
let b: bool = s.contains(42)
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1107"
        assert "expects 'str'" in excinfo.value.message


# =============================================================================
# Method Chaining Tests
# =============================================================================


class TestMethodChaining:
    """Tests for chaining multiple method calls."""

    def test_chain_trim_upper(self):
        """Can chain trim().upper()."""
        source = '''
let s: str = "  hello  "
print(s.trim().upper())
'''
        result = execute_and_capture(source)
        assert result == "HELLO"

    def test_chain_trim_split(self):
        """Can chain trim().split()."""
        source = '''
let s: str = "  a,b,c  "
let parts: [str] = s.trim().split(",")
print(parts[1])
'''
        result = execute_and_capture(source)
        assert result == "b"

    def test_chain_lower_replace(self):
        """Can chain lower().replace()."""
        source = '''
let s: str = "HELLO WORLD"
print(s.lower().replace("world", "quasar"))
'''
        result = execute_and_capture(source)
        assert result == "hello quasar"

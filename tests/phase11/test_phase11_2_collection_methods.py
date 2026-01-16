"""
Phase 11.2 — Collection Methods Tests.

Tests for List and Dict methods with generic type validation.

Test coverage:
- List: push, pop, contains, join, reverse, clear
- Dict: has_key, get, remove, clear, keys, values
- Generic type validation (E1100, E1102)
- Method chaining
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.semantic.errors import SemanticError
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
# List Methods
# =============================================================================


class TestListMethods:
    """Tests for list methods."""

    def test_push(self):
        """push() appends element to list."""
        source = '''
let nums: [int] = [1, 2, 3]
nums.push(4)
print(nums[3])
'''
        result = execute_and_capture(source)
        assert result == "4"

    def test_push_multiple(self):
        """push() can be called multiple times."""
        source = '''
let nums: [int] = []
nums.push(1)
nums.push(2)
nums.push(3)
print(nums.len())
'''
        result = execute_and_capture(source)
        assert result == "3"

    def test_pop(self):
        """pop() removes and returns last element."""
        source = '''
let nums: [int] = [1, 2, 3]
let last: int = nums.pop()
print(last)
print(nums.len())
'''
        result = execute_and_capture(source)
        assert result == "3\n2"

    def test_contains_true(self):
        """contains() returns true when element exists."""
        source = '''
let nums: [int] = [1, 2, 3]
print(nums.contains(2))
'''
        result = execute_and_capture(source)
        assert result == "True"

    def test_contains_false(self):
        """contains() returns false when element doesn't exist."""
        source = '''
let nums: [int] = [1, 2, 3]
print(nums.contains(5))
'''
        result = execute_and_capture(source)
        assert result == "False"

    def test_join(self):
        """join() concatenates string list with separator."""
        source = '''
let words: [str] = ["a", "b", "c"]
print(words.join(","))
'''
        result = execute_and_capture(source)
        assert result == "a,b,c"

    def test_join_space(self):
        """join() with space separator."""
        source = '''
let words: [str] = ["hello", "world"]
print(words.join(" "))
'''
        result = execute_and_capture(source)
        assert result == "hello world"

    def test_reverse(self):
        """reverse() reverses list in place."""
        source = '''
let nums: [int] = [1, 2, 3]
nums.reverse()
print(nums[0])
print(nums[2])
'''
        result = execute_and_capture(source)
        assert result == "3\n1"

    def test_clear(self):
        """clear() removes all elements."""
        source = '''
let nums: [int] = [1, 2, 3]
nums.clear()
print(nums.len())
'''
        result = execute_and_capture(source)
        assert result == "0"


# =============================================================================
# Dict Methods
# =============================================================================


class TestDictMethods:
    """Tests for dictionary methods."""

    def test_has_key_true(self):
        """has_key() returns true when key exists."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
print(d.has_key("a"))
'''
        result = execute_and_capture(source)
        assert result == "True"

    def test_has_key_false(self):
        """has_key() returns false when key doesn't exist."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
print(d.has_key("c"))
'''
        result = execute_and_capture(source)
        assert result == "False"

    def test_get_existing(self):
        """get() returns value for existing key."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
print(d.get("a", 0))
'''
        result = execute_and_capture(source)
        assert result == "1"

    def test_get_missing_with_default(self):
        """get() returns default for missing key."""
        source = '''
let d: Dict[str, int] = {"a": 1}
print(d.get("missing", 42))
'''
        result = execute_and_capture(source)
        assert result == "42"

    def test_remove(self):
        """remove() deletes key from dict."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
d.remove("a")
print(d.has_key("a"))
print(d.len())
'''
        result = execute_and_capture(source)
        assert result == "False\n1"

    def test_clear(self):
        """clear() removes all entries."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
d.clear()
print(d.len())
'''
        result = execute_and_capture(source)
        assert result == "0"

    def test_keys(self):
        """keys() returns list of keys."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
let k: [str] = d.keys()
print(k.len())
'''
        result = execute_and_capture(source)
        assert result == "2"

    def test_values(self):
        """values() returns list of values."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
let v: [int] = d.values()
print(v.len())
'''
        result = execute_and_capture(source)
        assert result == "2"


# =============================================================================
# Generic Type Validation
# =============================================================================


class TestGenericTypeValidation:
    """Tests for generic type checking."""

    def test_error_e1100_push_wrong_type(self):
        """E1100: push() with wrong element type."""
        source = '''
let nums: [int] = [1, 2, 3]
nums.push("hello")
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1100"
        assert "expects element type 'int'" in excinfo.value.message

    def test_error_e1100_contains_wrong_type(self):
        """E1100: contains() with wrong element type."""
        source = '''
let nums: [int] = [1, 2, 3]
let b: bool = nums.contains("hello")
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1100"

    def test_error_e1102_join_non_string_list(self):
        """E1102: join() only works on [str]."""
        source = '''
let nums: [int] = [1, 2, 3]
let s: str = nums.join(",")
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1102"
        assert "join() only works on [str]" in excinfo.value.message

    def test_error_e1100_dict_has_key_wrong_type(self):
        """E1100: has_key() with wrong key type."""
        source = '''
let d: Dict[str, int] = {"a": 1}
let b: bool = d.has_key(42)
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1100"
        assert "expects key type 'str'" in excinfo.value.message

    def test_error_e1100_dict_get_wrong_default_type(self):
        """E1100: get() with wrong default value type."""
        source = '''
let d: Dict[str, int] = {"a": 1}
let v: int = d.get("b", "wrong")
'''
        with pytest.raises(SemanticError) as excinfo:
            analyze_only(source)
        assert excinfo.value.code == "E1100"
        assert "expects value type 'int'" in excinfo.value.message


# =============================================================================
# Code Generation
# =============================================================================


class TestCodeGen:
    """Tests for correct Python code generation."""

    def test_codegen_push_to_append(self):
        """push() generates .append()."""
        source = '''
let nums: [int] = [1]
nums.push(2)
'''
        code = compile_to_python(source)
        assert 'nums.append(2)' in code

    def test_codegen_contains_to_in(self):
        """List contains() generates 'in' operator."""
        source = '''
let nums: [int] = [1, 2, 3]
let b: bool = nums.contains(2)
'''
        code = compile_to_python(source)
        assert 'b = (2 in nums)' in code

    def test_codegen_join_inverted(self):
        """join() inverts to Python's sep.join(list)."""
        source = '''
let words: [str] = ["a", "b"]
let s: str = words.join(",")
'''
        code = compile_to_python(source)
        assert 's = ",".join(words)' in code

    def test_codegen_has_key_to_in(self):
        """has_key() generates 'in' operator."""
        source = '''
let d: Dict[str, int] = {"a": 1}
let b: bool = d.has_key("a")
'''
        code = compile_to_python(source)
        assert 'b = ("a" in d)' in code

    def test_codegen_remove_to_pop(self):
        """remove() generates .pop(k, None)."""
        source = '''
let d: Dict[str, int] = {"a": 1}
d.remove("a")
'''
        code = compile_to_python(source)
        assert 'd.pop("a", None)' in code

    def test_codegen_keys(self):
        """keys() generates list(d.keys())."""
        source = '''
let d: Dict[str, int] = {"a": 1}
let k: [str] = d.keys()
'''
        code = compile_to_python(source)
        assert 'k = list(d.keys())' in code

    def test_codegen_values(self):
        """values() generates list(d.values())."""
        source = '''
let d: Dict[str, int] = {"a": 1}
let v: [int] = d.values()
'''
        code = compile_to_python(source)
        assert 'v = list(d.values())' in code


# =============================================================================
# Method Chaining
# =============================================================================


class TestMethodChaining:
    """Tests for chaining collection methods."""

    def test_chain_keys_len(self):
        """Can chain d.keys().len()."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2, "c": 3}
print(d.keys().len())
'''
        result = execute_and_capture(source)
        assert result == "3"

    def test_chain_values_contains(self):
        """Can chain d.values().contains()."""
        source = '''
let d: Dict[str, int] = {"a": 1, "b": 2}
print(d.values().contains(2))
'''
        result = execute_and_capture(source)
        assert result == "True"

    def test_chain_split_join(self):
        """Can chain string split/join."""
        source = '''
let s: str = "a,b,c"
let parts: [str] = s.split(",")
let rejoined: str = parts.join("-")
print(rejoined)
'''
        result = execute_and_capture(source)
        assert result == "a-b-c"

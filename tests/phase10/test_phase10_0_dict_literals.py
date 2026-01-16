"""
Phase 10.0 — Dictionary Literals Tests.

Tests for dictionary type annotations, dict literals, and semantic validation.

Test coverage:
- Dict[K, V] type annotation parsing
- Dict literal parsing: { key: value, ... }
- Empty dict literals: {}
- Trailing commas in dict literals
- Semantic validation: homogeneous keys (E1000)
- Semantic validation: homogeneous values (E1001)
- Semantic validation: hashable keys only (E1002)
- Code generation: dict literals to Python dicts
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator
from quasar.ast import (
    DictType,
    DictLiteral,
    DictEntry,
    INT,
    STR,
    BOOL,
    FLOAT,
    is_dict,
    is_hashable,
)


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


def parse_only(source: str):
    """Helper to only parse source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def analyze_only(source: str):
    """Helper to parse and analyze source code."""
    ast = parse_only(source)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return ast


# =============================================================================
# Type Helper Tests
# =============================================================================


class TestTypeHelpers:
    """Tests for dict type helper functions."""

    def test_is_dict_true(self):
        """is_dict returns True for DictType."""
        assert is_dict(DictType(INT, STR)) is True

    def test_is_dict_false_for_primitives(self):
        """is_dict returns False for primitive types."""
        assert is_dict(INT) is False
        assert is_dict(STR) is False
        assert is_dict(BOOL) is False
        assert is_dict(FLOAT) is False

    def test_is_hashable_primitives(self):
        """Primitive types int, str, bool are hashable."""
        assert is_hashable(INT) is True
        assert is_hashable(STR) is True
        assert is_hashable(BOOL) is True

    def test_is_hashable_float(self):
        """float is hashable (in Python it is)."""
        assert is_hashable(FLOAT) is True

    def test_is_hashable_list_false(self):
        """List types are not hashable."""
        from quasar.ast import ListType
        assert is_hashable(ListType(INT)) is False

    def test_is_hashable_dict_false(self):
        """Dict types are not hashable."""
        assert is_hashable(DictType(INT, STR)) is False


# =============================================================================
# Parser Tests - Type Annotations
# =============================================================================


class TestDictTypeAnnotation:
    """Tests for Dict[K, V] type annotation parsing."""

    def test_dict_int_str_annotation(self):
        """Parse Dict[int, str] type annotation."""
        source = 'let d: Dict[int, str] = {"a": "b"}'
        ast = parse_only(source)
        assert len(ast.declarations) == 1
        decl = ast.declarations[0]
        assert isinstance(decl.type_annotation, DictType)
        assert decl.type_annotation.key_type == INT
        assert decl.type_annotation.value_type == STR

    def test_dict_str_int_annotation(self):
        """Parse Dict[str, int] type annotation."""
        source = 'let d: Dict[str, int] = {"key": 42}'
        ast = parse_only(source)
        decl = ast.declarations[0]
        assert isinstance(decl.type_annotation, DictType)
        assert decl.type_annotation.key_type == STR
        assert decl.type_annotation.value_type == INT

    def test_dict_str_bool_annotation(self):
        """Parse Dict[str, bool] type annotation."""
        source = 'let d: Dict[str, bool] = {"flag": true}'
        ast = parse_only(source)
        decl = ast.declarations[0]
        assert isinstance(decl.type_annotation, DictType)
        assert decl.type_annotation.key_type == STR
        assert decl.type_annotation.value_type == BOOL


# =============================================================================
# Parser Tests - Dict Literals
# =============================================================================


class TestDictLiteralParsing:
    """Tests for dict literal parsing."""

    def test_empty_dict_literal(self):
        """Parse empty dict literal: {}"""
        source = 'let d: Dict[str, int] = {}'
        ast = parse_only(source)
        decl = ast.declarations[0]
        assert isinstance(decl.initializer, DictLiteral)
        assert len(decl.initializer.entries) == 0

    def test_single_entry_dict(self):
        """Parse dict with single entry."""
        source = 'let d: Dict[str, int] = {"key": 42}'
        ast = parse_only(source)
        decl = ast.declarations[0]
        assert isinstance(decl.initializer, DictLiteral)
        assert len(decl.initializer.entries) == 1

    def test_multiple_entries_dict(self):
        """Parse dict with multiple entries."""
        source = 'let d: Dict[str, int] = {"a": 1, "b": 2, "c": 3}'
        ast = parse_only(source)
        decl = ast.declarations[0]
        assert isinstance(decl.initializer, DictLiteral)
        assert len(decl.initializer.entries) == 3

    def test_trailing_comma_dict(self):
        """Parse dict with trailing comma."""
        source = 'let d: Dict[str, int] = {"a": 1, "b": 2,}'
        ast = parse_only(source)
        decl = ast.declarations[0]
        assert isinstance(decl.initializer, DictLiteral)
        assert len(decl.initializer.entries) == 2

    def test_int_keys_dict(self):
        """Parse dict with int keys."""
        source = 'let d: Dict[int, str] = {1: "one", 2: "two"}'
        ast = parse_only(source)
        decl = ast.declarations[0]
        assert isinstance(decl.initializer, DictLiteral)
        assert len(decl.initializer.entries) == 2


# =============================================================================
# Semantic Analysis Tests - Success Cases
# =============================================================================


class TestDictSemanticSuccess:
    """Tests for successful semantic analysis of dicts."""

    def test_dict_str_int_valid(self):
        """Valid Dict[str, int] with string keys and int values."""
        source = 'let d: Dict[str, int] = {"a": 1, "b": 2}'
        analyze_only(source)  # Should not raise

    def test_dict_int_str_valid(self):
        """Valid Dict[int, str] with int keys and string values."""
        source = 'let d: Dict[int, str] = {1: "one", 2: "two"}'
        analyze_only(source)  # Should not raise

    def test_dict_bool_int_valid(self):
        """Valid Dict[bool, int] with bool keys."""
        source = 'let d: Dict[bool, int] = {true: 1, false: 0}'
        analyze_only(source)  # Should not raise

    def test_empty_dict_with_annotation(self):
        """Empty dict is valid when type annotation is provided."""
        source = 'let d: Dict[str, int] = {}'
        analyze_only(source)  # Should not raise


# =============================================================================
# Semantic Analysis Tests - Error Cases
# =============================================================================


class TestDictSemanticErrors:
    """Tests for semantic errors with dicts."""

    def test_heterogeneous_keys_error(self):
        """E1000: Dict with mixed key types should fail."""
        source = 'let d: Dict[str, int] = {"a": 1, 2: 2}'
        with pytest.raises(Exception) as exc_info:
            analyze_only(source)
        assert "E1000" in str(exc_info.value)

    def test_heterogeneous_values_error(self):
        """E1001: Dict with mixed value types should fail."""
        source = 'let d: Dict[str, int] = {"a": 1, "b": "two"}'
        with pytest.raises(Exception) as exc_info:
            analyze_only(source)
        assert "E1001" in str(exc_info.value)

    def test_list_key_error(self):
        """E1002: List keys are not hashable."""
        source = 'let d: Dict[[int], str] = {[1, 2]: "test"}'
        with pytest.raises(Exception) as exc_info:
            analyze_only(source)
        assert "E1002" in str(exc_info.value)


# =============================================================================
# Code Generation Tests
# =============================================================================


class TestDictCodeGen:
    """Tests for dict code generation."""

    def test_empty_dict_codegen(self):
        """Empty dict generates {}."""
        source = 'let d: Dict[str, int] = {}'
        code = compile_to_python(source)
        assert "d = {}" in code

    def test_single_entry_dict_codegen(self):
        """Single entry dict generates {k: v}."""
        source = 'let d: Dict[str, int] = {"key": 42}'
        code = compile_to_python(source)
        assert 'd = {"key": 42}' in code

    def test_multiple_entries_dict_codegen(self):
        """Multiple entries dict generates proper Python dict."""
        source = 'let d: Dict[str, int] = {"a": 1, "b": 2}'
        code = compile_to_python(source)
        assert 'd = {"a": 1, "b": 2}' in code

    def test_int_keys_dict_codegen(self):
        """Int keys dict generates proper Python dict."""
        source = 'let d: Dict[int, str] = {1: "one", 2: "two"}'
        code = compile_to_python(source)
        assert 'd = {1: "one", 2: "two"}' in code

    def test_bool_keys_dict_codegen(self):
        """Bool keys dict generates proper Python dict."""
        source = 'let d: Dict[bool, int] = {true: 1, false: 0}'
        code = compile_to_python(source)
        assert "d = {True: 1, False: 0}" in code


# =============================================================================
# DictType String Representation
# =============================================================================


class TestDictTypeStr:
    """Tests for DictType string representation."""

    def test_dict_type_str_int_str(self):
        """DictType str() returns Dict[int, str]."""
        dt = DictType(INT, STR)
        assert str(dt) == "Dict[int, str]"

    def test_dict_type_str_str_bool(self):
        """DictType str() returns Dict[str, bool]."""
        dt = DictType(STR, BOOL)
        assert str(dt) == "Dict[str, bool]"

"""
Phase 12.1 Tests: Enum Semantic Analysis

Tests for enum type checking, error codes E1200-E1205, and type resolution.
"""
import pytest
from quasar.lexer.lexer import Lexer
from quasar.parser.parser import Parser
from quasar.semantic.analyzer import SemanticAnalyzer
from quasar.semantic.errors import SemanticError
from quasar.ast.types import EnumType


def analyze(source: str):
    """Parse and analyze source."""
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    program = parser.parse()
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)


# ============================================================================
# Valid Enum Declaration Tests
# ============================================================================

def test_enum_decl_valid():
    """Valid enum declaration is accepted."""
    program = analyze("enum Color { Red, Green, Blue }")
    assert len(program.declarations) == 1


def test_enum_access_valid():
    """Enum variant access is valid."""
    source = """
    enum Color { Red, Green, Blue }
    let c: Color = Color.Red
    """
    program = analyze(source)
    assert len(program.declarations) == 2


def test_enum_const_decl():
    """Const with enum type works."""
    source = """
    enum Status { Ok, Err }
    const DEFAULT: Status = Status.Ok
    """
    program = analyze(source)
    assert len(program.declarations) == 2


def test_enum_fn_param():
    """Function parameter with enum type works."""
    source = """
    enum Status { Ok, Err }
    fn check(s: Status) -> bool {
        return s == Status.Ok
    }
    """
    analyze(source)  # Should not raise


def test_enum_fn_return():
    """Function returning enum type works."""
    source = """
    enum Status { Ok, Err }
    fn get_status() -> Status {
        return Status.Ok
    }
    """
    analyze(source)  # Should not raise


def test_enum_equality_same_type():
    """Enum == comparison with same type works."""
    source = """
    enum Color { Red, Blue }
    let r: bool = Color.Red == Color.Blue
    """
    analyze(source)  # Should not raise


def test_enum_inequality():
    """Enum != comparison works."""
    source = """
    enum Color { Red, Blue }
    let r: bool = Color.Red != Color.Blue
    """
    analyze(source)  # Should not raise


def test_enum_in_if_condition():
    """Enum comparison in if condition works."""
    source = """
    enum Light { Red, Green }
    let l: Light = Light.Red
    if l == Light.Red {
        print("stop")
    }
    """
    analyze(source)  # Should not raise


# ============================================================================
# Error Tests: E1200 - Redeclaration of Type
# ============================================================================

def test_E1200_duplicate_enum():
    """E1200: Duplicate enum name."""
    source = """
    enum Color { Red }
    enum Color { Blue }
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E1200"


def test_E1200_enum_struct_conflict():
    """E1200: Enum name conflicts with struct."""
    source = """
    struct Point { x: int }
    enum Point { A, B }
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E1200"


# ============================================================================
# Error Tests: E1201 - Duplicate Variant
# ============================================================================

def test_E1201_duplicate_variant():
    """E1201: Duplicate variant in same enum."""
    source = "enum Color { Red, Red }"
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E1201"
    assert "Red" in excinfo.value.message


def test_E1201_multiple_duplicates():
    """E1201: Reports first duplicate."""
    source = "enum Status { A, B, A, B }"
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E1201"


# ============================================================================
# Error Tests: E1202 - Unknown Variant
# ============================================================================

def test_E1202_unknown_variant():
    """E1202: Unknown variant for enum type."""
    source = """
    enum Color { Red, Green }
    let c: Color = Color.Purple
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E1202"
    assert "Purple" in excinfo.value.message


# ============================================================================
# Error Tests: E1204 - Different Enum Comparison
# ============================================================================

def test_E1204_compare_different_enums():
    """E1204: Cannot compare different enum types."""
    source = """
    enum Color { Red }
    enum Status { Active }
    let c: Color = Color.Red
    let s: Status = Status.Active
    let x: bool = c == s
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E1204"


def test_E1204_enum_vs_non_enum():
    """E1204: Cannot compare enum with non-enum."""
    source = """
    enum Color { Red }
    let c: Color = Color.Red
    let x: bool = c == 1
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E1204"


# ============================================================================
# Error Tests: E1205 - Invalid Operator for Enum
# ============================================================================

def test_E1205_enum_less_than():
    """E1205: Enum < is not allowed."""
    source = """
    enum Color { Red, Blue }
    let r: bool = Color.Red < Color.Blue
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E1205"


def test_E1205_enum_greater_than():
    """E1205: Enum > is not allowed."""
    source = """
    enum Color { Red, Blue }
    let r: bool = Color.Red > Color.Blue
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E1205"


def test_E1205_enum_less_equal():
    """E1205: Enum <= is not allowed."""
    source = """
    enum Color { Red, Blue }
    let r: bool = Color.Red <= Color.Blue
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E1205"


def test_E1205_enum_greater_equal():
    """E1205: Enum >= is not allowed."""
    source = """
    enum Color { Red, Blue }
    let r: bool = Color.Red >= Color.Blue
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E1205"


# ============================================================================
# Type Mismatch Tests
# ============================================================================

def test_wrong_enum_assignment():
    """E0100: Cannot assign wrong enum type."""
    source = """
    enum Color { Red }
    enum Size { Big }
    let c: Color = Size.Big
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0100"

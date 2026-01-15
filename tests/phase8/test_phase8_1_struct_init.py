"""
Phase 8.1 Tests: Struct Instantiation

Tests valid instantiation, field order, errors E0803-E0806, and code generation.
"""
import pytest
from quasar.parser.parser import Parser
from quasar.lexer.lexer import Lexer
from quasar.semantic.analyzer import SemanticAnalyzer
from quasar.codegen.generator import CodeGenerator
from quasar.semantic.errors import SemanticError


def parse(source):
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    return parser.parse()


def analyze(source):
    program = parse(source)
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)


def generate(source):
    program = analyze(source)
    generator = CodeGenerator()
    return generator.generate(program)


# ============================================================================
# Valid Instantiation Tests
# ============================================================================

def test_struct_init_valid():
    """Basic valid struct instantiation."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1, y: 2 }
    """
    program = analyze(source)
    assert len(program.declarations) == 2


def test_struct_init_different_field_order():
    """Fields can be in any order (named initialization)."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { y: 2, x: 1 }
    """
    program = analyze(source)
    assert len(program.declarations) == 2


def test_struct_init_with_expressions():
    """Field values can be expressions."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1 + 1, y: 2 * 3 }
    """
    program = analyze(source)
    assert len(program.declarations) == 2


def test_struct_init_with_variables():
    """Field values can be variables."""
    source = """
    struct Point { x: int, y: int }
    let a: int = 10
    let b: int = 20
    let p: Point = Point { x: a, y: b }
    """
    program = analyze(source)
    assert len(program.declarations) == 4


def test_struct_init_mixed_types():
    """Struct with multiple field types."""
    source = """
    struct User {
        name: str,
        age: int,
        active: bool
    }
    let u: User = User { name: "Alice", age: 30, active: true }
    """
    program = analyze(source)
    assert len(program.declarations) == 2


# ============================================================================
# Error Tests
# ============================================================================

def test_error_struct_not_defined():
    """E0803: Struct must be defined before use."""
    source = 'let p: Point = Point { x: 1, y: 2 }'
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0803"


def test_error_missing_field():
    """E0804: All fields must be provided."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1 }
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0804"
    assert "y" in excinfo.value.message


def test_error_unknown_field():
    """E0805: Unknown fields are not allowed."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1, y: 2, z: 3 }
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0805"
    assert "z" in excinfo.value.message


def test_error_field_type_mismatch():
    """E0806: Field types must match declaration."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: "hello", y: 2 }
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0806"


def test_error_multiple_missing_fields():
    """E0804: Reports all missing fields."""
    source = """
    struct User { name: str, age: int, active: bool }
    let u: User = User { name: "Alice" }
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0804"


# ============================================================================
# Code Generation Tests
# ============================================================================

def test_codegen_struct_init():
    """Generated Python uses keyword arguments."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1, y: 2 }
    """
    code = generate(source)
    assert "Point(x=1, y=2)" in code


def test_codegen_struct_init_with_expression():
    """Expressions in field values are generated correctly."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1 + 1, y: 2 }
    """
    code = generate(source)
    # Expressions have defensive parentheses
    assert "Point(x=(1 + 1), y=2)" in code


def test_codegen_multiple_structs():
    """Multiple struct types work together."""
    source = """
    struct Point { x: int, y: int }
    struct Size { w: int, h: int }
    let p: Point = Point { x: 0, y: 0 }
    let s: Size = Size { w: 100, h: 200 }
    """
    code = generate(source)
    assert "Point(x=0, y=0)" in code
    assert "Size(w=100, h=200)" in code

"""
Phase 8.2 Tests: Member Access (Dot Notation)

Tests reading/writing struct fields, chaining, and errors E0807-E0809.
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
# Read Access Tests
# ============================================================================

def test_member_read():
    """Basic field read."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1, y: 2 }
    let x: int = p.x
    """
    program = analyze(source)
    assert len(program.declarations) == 3


def test_member_read_in_expression():
    """Field read in arithmetic expression."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 3, y: 4 }
    let sum: int = p.x + p.y
    """
    program = analyze(source)
    assert len(program.declarations) == 3


def test_member_read_in_print():
    """Field read in print."""
    source = """
    struct User { name: str }
    let u: User = User { name: "Alice" }
    print(u.name)
    """
    program = analyze(source)
    assert len(program.declarations) == 3


# ============================================================================
# Write Access Tests
# ============================================================================

def test_member_write():
    """Basic field write."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1, y: 2 }
    p.x = 10
    """
    program = analyze(source)
    assert len(program.declarations) == 3


def test_member_write_expression():
    """Field write with expression."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1, y: 2 }
    p.x = p.x + 1
    """
    program = analyze(source)
    assert len(program.declarations) == 3


# ============================================================================
# Error Tests
# ============================================================================

def test_error_member_access_on_primitive():
    """E0807: Cannot access field of primitive type."""
    source = """
    let x: int = 10
    let y: int = x.field
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0807"


def test_error_unknown_field_read():
    """E0808: Unknown field in read."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1, y: 2 }
    let z: int = p.z
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0808"


def test_error_unknown_field_write():
    """E0808: Unknown field in write."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1, y: 2 }
    p.z = 10
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0808"


def test_error_field_type_mismatch_write():
    """E0809: Type mismatch in field write."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1, y: 2 }
    p.x = "hello"
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0809"


# ============================================================================
# Code Generation Tests
# ============================================================================

def test_codegen_member_read():
    """Generated Python uses dot notation."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1, y: 2 }
    let v: int = p.x
    """
    code = generate(source)
    assert "p.x" in code


def test_codegen_member_write():
    """Generated Python uses dot assignment."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 1, y: 2 }
    p.x = 10
    """
    code = generate(source)
    assert "p.x = 10" in code


def test_codegen_member_math():
    """Generated Python with member access in expressions."""
    source = """
    struct Point { x: int, y: int }
    let p: Point = Point { x: 3, y: 4 }
    let sum: int = p.x + p.y
    """
    code = generate(source)
    assert "p.x" in code
    assert "p.y" in code

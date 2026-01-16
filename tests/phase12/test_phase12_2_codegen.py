"""
Phase 12.2 Tests: Enum Code Generation

Tests for generating Python Enum classes from Quasar enums.
"""
import pytest
from quasar.lexer.lexer import Lexer
from quasar.parser.parser import Parser
from quasar.semantic.analyzer import SemanticAnalyzer
from quasar.codegen.generator import CodeGenerator


def generate(source: str) -> str:
    """Compile Quasar source to Python code."""
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    program = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    generator = CodeGenerator()
    return generator.generate(program)


# ============================================================================
# Import Generation Tests
# ============================================================================

def test_enum_import_added():
    """Enum declaration adds 'from enum import Enum'."""
    code = generate("enum Color { Red }")
    assert "from enum import Enum" in code


def test_no_enum_import_when_not_needed():
    """No enum import when there are no enums."""
    code = generate("let x: int = 42")
    assert "from enum import Enum" not in code


def test_enum_and_struct_imports():
    """Both enum and struct imports are present when needed."""
    source = """
    enum Priority { Low, High }
    struct Task { name: str }
    """
    code = generate(source)
    assert "from enum import Enum" in code
    assert "from dataclasses import dataclass" in code


# ============================================================================
# Enum Class Generation Tests
# ============================================================================

def test_enum_class_generated():
    """Enum generates Python Enum class."""
    code = generate("enum Color { Red, Green, Blue }")
    assert "class Color(Enum):" in code


def test_enum_variants_as_strings():
    """Variants have string values."""
    code = generate("enum Color { Red, Green, Blue }")
    assert 'Red = "Red"' in code
    assert 'Green = "Green"' in code
    assert 'Blue = "Blue"' in code


def test_enum_single_variant():
    """Single variant enum works."""
    code = generate("enum Status { Ok }")
    assert "class Status(Enum):" in code
    assert 'Ok = "Ok"' in code


def test_enum_many_variants():
    """Many variants are all generated."""
    source = "enum Direction { North, East, South, West }"
    code = generate(source)
    assert 'North = "North"' in code
    assert 'East = "East"' in code
    assert 'South = "South"' in code
    assert 'West = "West"' in code


# ============================================================================
# Enum Usage Generation Tests
# ============================================================================

def test_enum_access_codegen():
    """Color.Red generates correctly."""
    source = """
    enum Color { Red }
    let c: Color = Color.Red
    """
    code = generate(source)
    assert "c = Color.Red" in code


def test_enum_comparison_codegen():
    """Enum comparison generates parenthesized expression."""
    source = """
    enum Light { Red, Green }
    let l: Light = Light.Red
    let is_red: bool = l == Light.Red
    """
    code = generate(source)
    assert "is_red = (l == Light.Red)" in code


def test_enum_in_if_codegen():
    """Enum comparison in if condition works."""
    source = """
    enum State { On, Off }
    let s: State = State.On
    if s == State.On {
        print("enabled")
    }
    """
    code = generate(source)
    assert "if (s == State.On):" in code


def test_enum_function_param_codegen():
    """Function with enum parameter generates correctly."""
    source = """
    enum Status { Ok, Err }
    fn check(s: Status) -> bool {
        return s == Status.Ok
    }
    """
    code = generate(source)
    assert "def check(s):" in code
    assert "return (s == Status.Ok)" in code


def test_enum_function_return_codegen():
    """Function returning enum generates correctly."""
    source = """
    enum Status { Ok, Err }
    fn get_ok() -> Status {
        return Status.Ok
    }
    """
    code = generate(source)
    assert "return Status.Ok" in code


# ============================================================================
# Multiple Enums Tests
# ============================================================================

def test_multiple_enums():
    """Multiple enums in same file work."""
    source = """
    enum Color { Red, Blue }
    enum Size { Small, Large }
    let c: Color = Color.Red
    let s: Size = Size.Small
    """
    code = generate(source)
    assert "class Color(Enum):" in code
    assert "class Size(Enum):" in code
    assert "c = Color.Red" in code
    assert "s = Size.Small" in code


def test_enum_with_struct():
    """Enum and struct in same file work together."""
    source = """
    enum Priority { Low, High }
    struct Task {
        name: str,
        priority: Priority
    }
    """
    code = generate(source)
    assert "class Priority(Enum):" in code
    assert "@dataclass" in code
    assert "class Task:" in code

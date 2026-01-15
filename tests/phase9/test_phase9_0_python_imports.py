"""
Phase 9.0 Tests: Python Imports

Tests importing Python standard library modules.
"""
import pytest
from quasar.parser.parser import Parser
from quasar.lexer.lexer import Lexer
from quasar.semantic.analyzer import SemanticAnalyzer
from quasar.codegen.generator import CodeGenerator
from quasar.semantic.errors import SemanticError
from quasar.ast import ImportDecl


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
# Parser Tests
# ============================================================================

def test_parse_import_math():
    """Parse: import math"""
    source = "import math"
    program = parse(source)
    assert len(program.declarations) == 1
    assert isinstance(program.declarations[0], ImportDecl)
    assert program.declarations[0].module == "math"
    assert program.declarations[0].is_local == False


def test_parse_import_random():
    """Parse: import random"""
    source = "import random"
    program = parse(source)
    assert program.declarations[0].module == "random"


def test_parse_import_local():
    """Parse: import local file (future Phase 9.1)"""
    source = 'import "./utils.qsr"'
    program = parse(source)
    assert program.declarations[0].module == "./utils.qsr"
    assert program.declarations[0].is_local == True


# ============================================================================
# Semantic Tests
# ============================================================================

def test_semantic_import_math():
    """Semantic: import math is valid."""
    source = "import math"
    program = analyze(source)
    assert len(program.declarations) == 1


def test_semantic_use_module_member():
    """Semantic: Use math.sqrt allowed."""
    source = """
    import math
    let x: float = math.sqrt(16.0)
    """
    program = analyze(source)
    assert len(program.declarations) == 2


def test_semantic_use_math_pi():
    """Semantic: Use math.pi (constant)."""
    source = """
    import math
    let pi_val: float = math.pi
    """
    program = analyze(source)
    assert len(program.declarations) == 2


def test_semantic_any_type_assignment():
    """Semantic: ANY type can be assigned to any type."""
    source = """
    import math
    let x: float = math.sqrt(4.0)
    let y: int = math.floor(3.14)
    let s: str = math.anything
    """
    program = analyze(source)
    assert len(program.declarations) == 4


def test_error_duplicate_import():
    """E0900: Duplicate import."""
    source = """
    import math
    import math
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0900"


def test_error_undeclared_module():
    """E0001: Using undeclared module."""
    source = """
    let x: float = math.sqrt(4.0)
    """
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0001"


# ============================================================================
# Code Generation Tests
# ============================================================================

def test_codegen_import_math():
    """Generated Python has: import math"""
    source = "import math"
    code = generate(source)
    assert "import math" in code


def test_codegen_import_random():
    """Generated Python has: import random"""
    source = "import random"
    code = generate(source)
    assert "import random" in code


def test_codegen_use_module():
    """Generated Python uses module.method()"""
    source = """
    import math
    let x: float = math.sqrt(16.0)
    """
    code = generate(source)
    assert "import math" in code
    assert "math.sqrt" in code


def test_codegen_local_import():
    """Generated Python for local import."""
    from unittest.mock import patch
    source = 'import "./utils.qsr"'
    program = parse(source)
    analyzer = SemanticAnalyzer()
    with patch('os.path.exists', return_value=True):
        analyzed = analyzer.analyze(program)
    generator = CodeGenerator()
    code = generator.generate(analyzed)
    assert "import utils" in code

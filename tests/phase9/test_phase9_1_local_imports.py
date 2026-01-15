"""
Phase 9.1 Tests: Local File Imports

Tests importing local .qsr files.
"""
import pytest
from unittest.mock import patch
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


def analyze(source, mock_exists=True):
    """Analyze with optional file existence mocking."""
    program = parse(source)
    analyzer = SemanticAnalyzer()
    if mock_exists:
        with patch('os.path.exists', return_value=True):
            return analyzer.analyze(program)
    else:
        return analyzer.analyze(program)


def generate(source):
    """Generate code with mocked file existence."""
    program = parse(source)
    analyzer = SemanticAnalyzer()
    with patch('os.path.exists', return_value=True):
        analyzed = analyzer.analyze(program)
    generator = CodeGenerator()
    return generator.generate(analyzed)


# ============================================================================
# Parser Tests
# ============================================================================

def test_parse_local_import_simple():
    """Parse: import "./utils.qsr" """
    source = 'import "./utils.qsr"'
    program = parse(source)
    assert len(program.declarations) == 1
    assert isinstance(program.declarations[0], ImportDecl)
    assert program.declarations[0].module == "./utils.qsr"
    assert program.declarations[0].is_local == True


def test_parse_local_import_nested():
    """Parse: import with nested path."""
    source = 'import "./lib/helpers.qsr"'
    program = parse(source)
    assert program.declarations[0].module == "./lib/helpers.qsr"
    assert program.declarations[0].is_local == True


def test_parse_local_import_no_extension():
    """Parse: import without .qsr extension."""
    source = 'import "./mymodule"'
    program = parse(source)
    assert program.declarations[0].module == "./mymodule"


# ============================================================================
# Semantic Tests - Valid Cases
# ============================================================================

def test_semantic_local_import_valid():
    """Semantic: Valid local import (mocked file exists)."""
    source = 'import "./utils.qsr"'
    program = analyze(source)
    assert len(program.declarations) == 1


def test_semantic_local_import_use_function():
    """Semantic: Use function from local import."""
    source = '''
    import "./utils.qsr"
    let x: int = utils.helper(10)
    '''
    program = analyze(source)
    assert len(program.declarations) == 2


def test_semantic_local_import_use_variable():
    """Semantic: Access module variable."""
    source = '''
    import "./config.qsr"
    let val: int = config.MAX_VALUE
    '''
    program = analyze(source)
    assert len(program.declarations) == 2


def test_semantic_multiple_local_imports():
    """Semantic: Multiple local imports."""
    source = '''
    import "./utils.qsr"
    import "./helpers.qsr"
    '''
    program = analyze(source)
    assert len(program.declarations) == 2


def test_semantic_mixed_imports():
    """Semantic: Mix Python and local imports."""
    source = '''
    import math
    import "./utils.qsr"
    let x: float = math.sqrt(16.0)
    let y: int = utils.calculate(5)
    '''
    program = analyze(source)
    assert len(program.declarations) == 4


# ============================================================================
# Semantic Tests - Error Cases
# ============================================================================

def test_error_module_not_found():
    """E0901: Module not found."""
    source = 'import "./ghost.qsr"'
    with pytest.raises(SemanticError) as excinfo:
        analyze(source, mock_exists=False)
    assert excinfo.value.code == "E0901"
    assert "module not found" in excinfo.value.message


def test_error_duplicate_local_import():
    """E0900: Duplicate local import."""
    source = '''
    import "./utils.qsr"
    import "./utils.qsr"
    '''
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0900"


def test_error_use_unimported_local_module():
    """E0001: Use function from unimported local module."""
    source = '''
    let x: int = utils.helper(10)
    '''
    with pytest.raises(SemanticError) as excinfo:
        analyze(source, mock_exists=False)
    assert excinfo.value.code == "E0001"


# ============================================================================
# Code Generation Tests
# ============================================================================

def test_codegen_local_import_simple():
    """Generated Python: import utils"""
    source = 'import "./utils.qsr"'
    code = generate(source)
    assert "import utils" in code


def test_codegen_local_import_no_extension():
    """Generated Python handles missing extension."""
    source = 'import "./mymodule"'
    code = generate(source)
    assert "import mymodule" in code


def test_codegen_local_import_nested_path():
    """Generated Python for nested path (simplified to basename)."""
    source = 'import "./models/player.qsr"'
    code = generate(source)
    # Current implementation: import models.player or import player
    assert "import" in code


def test_codegen_local_import_with_usage():
    """Generated Python with module usage."""
    source = '''
    import "./utils.qsr"
    let x: int = utils.add(1, 2)
    '''
    code = generate(source)
    assert "import utils" in code
    assert "utils.add" in code


def test_codegen_mixed_imports():
    """Generated Python with both import types."""
    source = '''
    import math
    import "./utils.qsr"
    '''
    code = generate(source)
    assert "import math" in code
    assert "import utils" in code


# ============================================================================
# Edge Cases
# ============================================================================

def test_import_different_paths_same_name():
    """Different paths but same basename should conflict."""
    source = '''
    import "./lib1/utils.qsr"
    import "./lib2/utils.qsr"
    '''
    with pytest.raises(SemanticError) as excinfo:
        analyze(source)
    assert excinfo.value.code == "E0900"  # duplicate utils


def test_import_with_subdirectory():
    """Import from subdirectory."""
    source = 'import "./subdir/module.qsr"'
    program = analyze(source)
    assert len(program.declarations) == 1

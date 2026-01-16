"""
Phase 13.1 Canary Tests — File.exists

Tests to validate the static method call infrastructure works correctly
before implementing the full File API.
"""
import os
import pytest
import tempfile

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator


def analyze(source: str):
    """Helper to parse and analyze source code."""
    lexer = Lexer(source)
    program = Parser(lexer.tokenize()).parse()
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)


def generate(source: str) -> str:
    """Helper to parse and generate code from Quasar source."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    SemanticAnalyzer().analyze(ast)
    return CodeGenerator().generate(ast)


def compile_and_run(source: str, extra_globals: dict = None) -> dict:
    """Compile Quasar to Python and execute, returning locals."""
    code = generate(source)
    exec_globals = {"__builtins__": __builtins__}
    if extra_globals:
        exec_globals.update(extra_globals)
    exec_locals = {}
    exec(code, exec_globals, exec_locals)
    return exec_locals


class TestFileExistsSemantics:
    """Semantic analysis tests for File.exists."""

    def test_file_exists_returns_bool(self):
        """File.exists returns bool type."""
        source = """
let exists: bool = File.exists("test.txt")
"""
        # Should not raise - type is bool
        analyze(source)

    def test_file_exists_type_mismatch(self):
        """File.exists returns bool, not str."""
        source = """
let exists: str = File.exists("test.txt")
"""
        from quasar.semantic.errors import SemanticError
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0100"


class TestFileExistsCodeGen:
    """Code generation tests for File.exists."""

    def test_codegen_maps_to_os_path_exists(self):
        """File.exists(p) maps to _q_os.path.exists(p)."""
        source = """
let exists: bool = File.exists("test.txt")
"""
        code = generate(source)
        assert "_q_os.path.exists" in code
        assert 'exists = _q_os.path.exists("test.txt")' in code

    def test_import_os_included(self):
        """Generated code includes import os when File is used (aliased)."""
        source = """
let exists: bool = File.exists("test.txt")
"""
        code = generate(source)
        assert "import os as _q_os" in code
        lines = code.split("\n")
        assert lines[0] == "import os as _q_os"

    def test_no_import_os_when_file_not_used(self):
        """No import os when File is not used (regression check)."""
        source = """
let x: int = 42
"""
        code = generate(source)
        assert "import os" not in code
        assert code.strip() == "x = 42"


class TestFileExistsRuntime:
    """Runtime execution tests for File.exists."""

    def test_exists_true_for_existing_file(self):
        """File.exists returns true for existing file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            temp_path = f.name
            f.write(b"test content")

        try:
            source = f'''
let path: str = "{temp_path}"
let exists: bool = File.exists(path)
'''
            result = compile_and_run(source)
            assert result["exists"] is True
        finally:
            os.unlink(temp_path)

    def test_exists_false_for_nonexistent_file(self):
        """File.exists returns false for nonexistent file."""
        source = '''
let exists: bool = File.exists("/nonexistent/path/to/file.xyz")
'''
        result = compile_and_run(source)
        assert result["exists"] is False


class TestShadowingSafety:
    """Test that user code doesn't conflict with generated imports."""

    def test_user_os_variable_with_file_exists(self):
        """User can have variable named 'os' alongside File.exists.
        
        The generated import os should work correctly even if user 
        declares a variable with the same name later.
        """
        source = '''
let exists: bool = File.exists("/tmp")
let os: int = 42
'''
        code = generate(source)
        # Both should compile without conflict
        assert "import os as _q_os" in code
        assert "os = 42" in code
        
        # Run to verify no runtime conflict
        result = compile_and_run(source)
        assert result["os"] == 42
        # exists should have worked before os was shadowed
        assert result["exists"] is True  # /tmp usually exists


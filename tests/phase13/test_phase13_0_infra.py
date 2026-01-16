"""
Phase 13.0 Infrastructure Tests

Tests for builtin module protection (E0205) and static objects recognition.
"""
import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.semantic.errors import SemanticError
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
    return CodeGenerator().generate(ast)


class TestE0205ReservedIdentifiers:
    """E0205: Cannot shadow builtin modules (File, Env)."""

    def test_shadow_file_with_variable(self):
        """let File: int = 1 should be E0205."""
        source = """
fn test() -> void {
    let File: int = 1
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0205"
        assert "cannot shadow builtin module" in excinfo.value.message
        assert "File" in excinfo.value.message

    def test_shadow_env_with_variable(self):
        """let Env: str = "test" should be E0205."""
        source = """
fn test() -> void {
    let Env: str = "test"
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0205"
        assert "Env" in excinfo.value.message

    def test_shadow_file_with_struct(self):
        """struct File {} should be E0205."""
        source = """
struct File { x: int }
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0205"

    def test_shadow_env_with_struct(self):
        """struct Env {} should be E0205."""
        source = """
struct Env { value: str }
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0205"

    def test_shadow_file_with_function(self):
        """fn File() {} should be E0205."""
        source = """
fn File() -> void { }
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0205"

    def test_shadow_env_with_function(self):
        """fn Env() {} should be E0205."""
        source = """
fn Env() -> int {
    return 0
}
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0205"

    def test_shadow_file_with_parameter(self):
        """fn test(File: int) {} should be E0205."""
        source = """
fn test(File: int) -> void { }
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0205"

    def test_shadow_file_with_const(self):
        """const File: int = 1 should be E0205."""
        source = """
const File: int = 1
"""
        with pytest.raises(SemanticError) as excinfo:
            analyze(source)
        assert excinfo.value.code == "E0205"


class TestCodegenImports:
    """Test that os and sys are imported when File/Env are used."""

    def test_imports_os_and_sys_when_file_used(self):
        """Generated code should have imports when File is used."""
        source = """
let exists: bool = File.exists("test.txt")
"""
        result = generate(source)
        assert "import os as _q_os" in result
        assert "import sys as _q_sys" in result
        # Imports should be at the beginning
        lines = result.split("\n")
        assert lines[0] == "import os as _q_os"
        assert lines[1] == "import sys as _q_sys"

    def test_imports_os_and_sys_when_env_used(self):
        """Generated code should have imports when Env is used."""
        source = """
let home: str = Env.get("HOME", "/tmp")
"""
        result = generate(source)
        assert "import os as _q_os" in result
        assert "import sys as _q_sys" in result

    def test_no_imports_when_file_env_not_used(self):
        """No os/sys imports when File/Env are not used."""
        source = """
let x: int = 42
"""
        result = generate(source)
        assert "import os as _q_os" not in result
        assert "import sys as _q_sys" not in result
        assert result.strip() == "x = 42"

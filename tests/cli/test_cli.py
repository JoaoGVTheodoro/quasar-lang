"""
Tests for the Quasar CLI.
"""

import pytest
import tempfile
from pathlib import Path

from quasar.cli.main import main, create_parser, read_source, compile_source, check_source


class TestCLIParser:
    """Tests for CLI argument parsing."""
    
    def test_parser_creation(self):
        """Parser should be created successfully."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "quasar"
    
    def test_compile_command_parsing(self):
        """Should parse compile command with file argument."""
        parser = create_parser()
        args = parser.parse_args(["compile", "test.qsr"])
        assert args.command == "compile"
        assert args.file == "test.qsr"
        assert args.output is None
    
    def test_compile_with_output(self):
        """Should parse compile command with output option."""
        parser = create_parser()
        args = parser.parse_args(["compile", "test.qsr", "-o", "output.py"])
        assert args.command == "compile"
        assert args.file == "test.qsr"
        assert args.output == "output.py"
    
    def test_run_command_parsing(self):
        """Should parse run command."""
        parser = create_parser()
        args = parser.parse_args(["run", "test.qsr"])
        assert args.command == "run"
        assert args.file == "test.qsr"
    
    def test_check_command_parsing(self):
        """Should parse check command."""
        parser = create_parser()
        args = parser.parse_args(["check", "test.qsr"])
        assert args.command == "check"
        assert args.file == "test.qsr"
    
    def test_no_command(self):
        """Should have None command when no subcommand given."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.command is None


class TestReadSource:
    """Tests for source file reading."""
    
    def test_read_valid_file(self):
        """Should read content from valid file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qsr", delete=False) as f:
            f.write("let x: int = 42")
            f.flush()
            content = read_source(f.name)
            assert content == "let x: int = 42"
            Path(f.name).unlink()
    
    def test_read_nonexistent_file(self):
        """Should exit with error for nonexistent file."""
        with pytest.raises(SystemExit) as exc_info:
            read_source("/nonexistent/path/file.qsr")
        assert exc_info.value.code == 1


class TestCompileSource:
    """Tests for source compilation."""
    
    def test_compile_simple_declaration(self):
        """Should compile simple variable declaration."""
        source = "let x: int = 42"
        result = compile_source(source)
        assert "x = 42" in result
    
    def test_compile_function(self):
        """Should compile function declaration."""
        source = """fn add(a: int, b: int) -> int {
    return a + b
}"""
        result = compile_source(source)
        assert "def add(a, b):" in result
        assert "return a + b" in result
    
    def test_compile_invalid_syntax(self):
        """Should exit on syntax error."""
        with pytest.raises(SystemExit) as exc_info:
            compile_source("let x: int =")
        assert exc_info.value.code == 1
    
    def test_compile_semantic_error(self):
        """Should exit on semantic error."""
        with pytest.raises(SystemExit) as exc_info:
            compile_source("let x: int = true")
        assert exc_info.value.code == 1


class TestCheckSource:
    """Tests for source validation."""
    
    def test_check_valid_source(self):
        """Should return True for valid source."""
        source = "let x: int = 42"
        result = check_source(source)
        assert result is True
    
    def test_check_invalid_source(self):
        """Should exit on invalid source."""
        with pytest.raises(SystemExit) as exc_info:
            check_source("let x: int = true")
        assert exc_info.value.code == 1


class TestMainFunction:
    """Tests for the main CLI function."""
    
    def test_main_no_args(self):
        """Should return success with no arguments (shows help)."""
        result = main([])
        assert result == 0
    
    def test_main_compile_valid_file(self):
        """Should compile valid file successfully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qsr", delete=False) as f:
            f.write("let x: int = 42")
            f.flush()
            
            # Compile to temp output
            output_path = Path(f.name).with_suffix(".py")
            result = main(["compile", f.name])
            
            assert result == 0
            assert output_path.exists()
            
            # Cleanup
            Path(f.name).unlink()
            output_path.unlink()
    
    def test_main_check_valid_file(self):
        """Should check valid file successfully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qsr", delete=False) as f:
            f.write("let x: int = 42")
            f.flush()
            
            result = main(["check", f.name])
            assert result == 0
            
            Path(f.name).unlink()
    
    def test_main_run_valid_file(self):
        """Should run valid file successfully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qsr", delete=False) as f:
            # Simple program that doesn't produce output
            f.write("let x: int = 42")
            f.flush()
            
            result = main(["run", f.name])
            assert result == 0
            
            Path(f.name).unlink()
    
    def test_main_compile_invalid_file(self):
        """Should fail on invalid source."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qsr", delete=False) as f:
            f.write("let x: int = true")  # Type mismatch
            f.flush()
            
            with pytest.raises(SystemExit) as exc_info:
                main(["compile", f.name])
            assert exc_info.value.code == 1
            
            Path(f.name).unlink()


class TestEndToEnd:
    """End-to-end CLI tests."""
    
    def test_compile_and_verify_output(self):
        """Should generate valid Python code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qsr", delete=False) as f:
            f.write("""fn factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

let result: int = factorial(5)""")
            f.flush()
            
            output_path = Path(f.name).with_suffix(".py")
            result = main(["compile", f.name])
            
            assert result == 0
            
            # Verify generated code
            generated = output_path.read_text()
            assert "def factorial(n):" in generated
            assert "result = factorial(5)" in generated
            
            # Cleanup
            Path(f.name).unlink()
            output_path.unlink()
    
    def test_run_program_with_computation(self):
        """Should execute program correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qsr", delete=False) as f:
            f.write("""fn double(x: int) -> int {
    return x * 2
}

let value: int = double(21)""")
            f.flush()
            
            result = main(["run", f.name])
            assert result == 0
            
            Path(f.name).unlink()

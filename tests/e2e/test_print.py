"""
End-to-end tests for print statement (Phase 5).

These tests verify the complete pipeline from Quasar source to
executed Python output, including CLI integration.
"""

import pytest
import subprocess
import tempfile
from pathlib import Path

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator
from quasar.cli.main import main as cli_main


def compile_quasar(source: str) -> str:
    """Compile Quasar source to Python code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    generator = CodeGenerator()
    return generator.generate(ast)


def execute_python(code: str) -> str:
    """Execute Python code and capture output."""
    result = subprocess.run(
        ["python", "-c", code],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return result.stdout


def compile_and_run(source: str) -> str:
    """Compile Quasar source and execute the result."""
    python_code = compile_quasar(source)
    return execute_python(python_code)


class TestPrintE2E:
    """End-to-end tests for print functionality."""
    
    def test_print_int_output(self):
        """print(42) should output '42'"""
        output = compile_and_run("print(42)")
        assert output.strip() == "42"
    
    def test_print_float_output(self):
        """print(3.14) should output '3.14'"""
        output = compile_and_run("print(3.14)")
        assert output.strip() == "3.14"
    
    def test_print_true_output(self):
        """print(true) should output 'True'"""
        output = compile_and_run("print(true)")
        assert output.strip() == "True"
    
    def test_print_false_output(self):
        """print(false) should output 'False'"""
        output = compile_and_run("print(false)")
        assert output.strip() == "False"
    
    def test_print_string_output(self):
        """print("hello") should output 'hello'"""
        output = compile_and_run('print("hello")')
        assert output.strip() == "hello"
    
    def test_print_expression_output(self):
        """print(2 + 3) should output '5'"""
        output = compile_and_run("print(2 + 3)")
        assert output.strip() == "5"
    
    def test_print_variable_output(self):
        """print(x) should output variable value"""
        output = compile_and_run("let x: int = 100\nprint(x)")
        assert output.strip() == "100"
    
    def test_print_multiple_lines(self):
        """Multiple print statements should output multiple lines"""
        source = """print(1)
print(2)
print(3)"""
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines == ["1", "2", "3"]


class TestPrintWithFunctions:
    """Tests for print with function calls."""
    
    def test_print_function_result(self):
        """print(fn()) should output function result"""
        source = """fn double(n: int) -> int {
    return n * 2
}
print(double(21))"""
        output = compile_and_run(source)
        assert output.strip() == "42"
    
    def test_print_recursive_function(self):
        """print with recursive function result"""
        source = """fn factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}
print(factorial(5))"""
        output = compile_and_run(source)
        assert output.strip() == "120"
    
    def test_print_fibonacci(self):
        """print with fibonacci function"""
        source = """fn fib(n: int) -> int {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}
print(fib(10))"""
        output = compile_and_run(source)
        assert output.strip() == "55"


class TestPrintInControlFlow:
    """Tests for print in control flow structures."""
    
    def test_print_in_loop(self):
        """print inside loop should output each iteration"""
        source = """let i: int = 1
while i <= 3 {
    print(i)
    i = i + 1
}"""
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines == ["1", "2", "3"]
    
    def test_print_in_conditional_true(self):
        """print in if branch (condition true)"""
        source = """let x: int = 10
if x > 5 {
    print("big")
} else {
    print("small")
}"""
        output = compile_and_run(source)
        assert output.strip() == "big"
    
    def test_print_in_conditional_false(self):
        """print in else branch (condition false)"""
        source = """let x: int = 3
if x > 5 {
    print("big")
} else {
    print("small")
}"""
        output = compile_and_run(source)
        assert output.strip() == "small"


class TestPrintCLI:
    """Tests for print via CLI commands."""
    
    def test_cli_run_with_print(self):
        """quasar run should execute and show print output"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".qsr", delete=False
        ) as f:
            f.write('print("Hello from Quasar!")')
            f.flush()
            
            # Use subprocess to capture CLI output
            result = subprocess.run(
                ["python", "-m", "quasar", "run", f.name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            assert result.returncode == 0
            assert "Hello from Quasar!" in result.stdout
            
            Path(f.name).unlink()
    
    def test_cli_compile_then_run(self):
        """quasar compile then python execution"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".qsr", delete=False
        ) as f:
            f.write("print(42)")
            f.flush()
            
            qsr_path = Path(f.name)
            py_path = qsr_path.with_suffix(".py")
            
            # Compile
            compile_result = subprocess.run(
                ["python", "-m", "quasar", "compile", str(qsr_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert compile_result.returncode == 0
            
            # Run generated Python
            run_result = subprocess.run(
                ["python", str(py_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert run_result.stdout.strip() == "42"
            
            # Cleanup
            qsr_path.unlink()
            py_path.unlink()
    
    def test_cli_check_print_valid(self):
        """quasar check should validate print syntax"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".qsr", delete=False
        ) as f:
            f.write("print(123)")
            f.flush()
            
            result = subprocess.run(
                ["python", "-m", "quasar", "check", f.name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            assert result.returncode == 0
            assert "Valid" in result.stdout
            
            Path(f.name).unlink()


class TestPrintComplexPrograms:
    """Tests for print in complex real-world programs."""
    
    def test_countdown_with_print(self):
        """Countdown program with print"""
        source = """let count: int = 5
while count > 0 {
    print(count)
    count = count - 1
}
print(0)"""
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines == ["5", "4", "3", "2", "1", "0"]
    
    def test_fizzbuzz_simplified(self):
        """Simplified fizzbuzz-style program"""
        source = """let i: int = 1
while i <= 5 {
    if i % 2 == 0 {
        print("even")
    } else {
        print("odd")
    }
    i = i + 1
}"""
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines == ["odd", "even", "odd", "even", "odd"]
    
    def test_sum_with_print(self):
        """Sum calculation with final print"""
        source = """fn sum_to(n: int) -> int {
    let total: int = 0
    let i: int = 1
    while i <= n {
        total = total + i
        i = i + 1
    }
    return total
}
print(sum_to(10))"""
        output = compile_and_run(source)
        assert output.strip() == "55"

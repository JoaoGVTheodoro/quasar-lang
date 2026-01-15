"""
End-to-end integration tests for extended print (Phase 5.1).

These tests verify the complete pipeline for:
- Multiple arguments
- sep parameter
- end parameter
- Real-world use cases from PHASE5_1_DESIGN.md
"""

import pytest
import subprocess

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator


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


class TestMultipleArgumentsE2E:
    """E2E tests for print with multiple arguments."""
    
    def test_print_two_ints(self):
        """print(1, 2) should output '1 2'"""
        output = compile_and_run("print(1, 2)")
        assert output.strip() == "1 2"
    
    def test_print_three_ints(self):
        """print(1, 2, 3) should output '1 2 3'"""
        output = compile_and_run("print(1, 2, 3)")
        assert output.strip() == "1 2 3"
    
    def test_print_mixed_types(self):
        """print with mixed types should work correctly."""
        output = compile_and_run('print("Value:", 42, true, 3.14)')
        assert output.strip() == "Value: 42 True 3.14"
    
    def test_print_variables_multiple(self):
        """print with multiple variables."""
        source = """let a: int = 10
let b: int = 20
let c: int = 30
print(a, b, c)"""
        output = compile_and_run(source)
        assert output.strip() == "10 20 30"
    
    def test_print_expressions_multiple(self):
        """print with multiple expressions."""
        output = compile_and_run("print(1 + 1, 2 * 2, 3 - 1)")
        assert output.strip() == "2 4 2"


class TestSepParameterE2E:
    """E2E tests for print with sep parameter."""
    
    def test_print_sep_comma(self):
        """print with sep=',' should separate with comma."""
        output = compile_and_run('print(1, 2, 3, sep=",")')
        assert output.strip() == "1,2,3"
    
    def test_print_sep_dash(self):
        """print with sep='-' should separate with dash."""
        output = compile_and_run('print("a", "b", "c", sep="-")')
        assert output.strip() == "a-b-c"
    
    def test_print_sep_empty(self):
        """print with sep='' should concatenate."""
        output = compile_and_run('print(1, 2, 3, sep="")')
        assert output.strip() == "123"
    
    def test_print_sep_space_explicit(self):
        """print with sep=' ' (explicit default)."""
        output = compile_and_run('print(1, 2, 3, sep=" ")')
        assert output.strip() == "1 2 3"
    
    def test_print_sep_newline(self):
        """print with sep='\\n' should separate with newlines."""
        output = compile_and_run('print(1, 2, 3, sep="\\n")')
        assert output.strip() == "1\n2\n3"


class TestEndParameterE2E:
    """E2E tests for print with end parameter."""
    
    def test_print_end_empty(self):
        """print with end='' should not add newline."""
        source = '''print("a", end="")
print("b", end="")
print("c")'''
        output = compile_and_run(source)
        assert output.strip() == "abc"
    
    def test_print_end_custom(self):
        """print with end='!' should end with exclamation."""
        output = compile_and_run('print("hello", end="!")')
        assert output == "hello!"
    
    def test_print_end_double_newline(self):
        """print with end='\\n\\n' should add blank line."""
        output = compile_and_run('print("line1", end="\\n\\n")')
        assert output == "line1\n\n"


class TestSepAndEndCombinedE2E:
    """E2E tests for print with both sep and end."""
    
    def test_print_sep_and_end_together(self):
        """print with both sep and end."""
        output = compile_and_run('print(1, 2, 3, sep="-", end="!")')
        assert output == "1-2-3!"
    
    def test_print_csv_style(self):
        """CSV-style output with sep=','."""
        source = '''print("Name", "Age", "City", sep=",")
print("Alice", 30, "NYC", sep=",")
print("Bob", 25, "LA", sep=",")'''
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines[0] == "Name,Age,City"
        assert lines[1] == "Alice,30,NYC"
        assert lines[2] == "Bob,25,LA"


class TestRealWorldScenariosE2E:
    """E2E tests for real-world use cases from design doc."""
    
    def test_factorial_with_label(self):
        """Factorial example with labeled output."""
        source = """fn factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

let result: int = factorial(5)
print("Factorial =", result)"""
        output = compile_and_run(source)
        assert output.strip() == "Factorial = 120"
    
    def test_fibonacci_with_sep(self):
        """Fibonacci sequence with custom separator."""
        source = """fn fib(n: int) -> int {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

print(fib(0), fib(1), fib(2), fib(3), fib(4), fib(5), sep=", ")"""
        output = compile_and_run(source)
        assert output.strip() == "0, 1, 1, 2, 3, 5"
    
    def test_inline_loading_simulation(self):
        """Simulate inline loading with end=''."""
        source = '''print("Loading", end="")
print(".", end="")
print(".", end="")
print(".", end="")
print(" Done!")'''
        output = compile_and_run(source)
        assert output.strip() == "Loading... Done!"
    
    def test_progress_dots(self):
        """Progress indicator with dots."""
        source = '''let i: int = 0
while i < 3 {
    print(".", end="")
    i = i + 1
}
print(" complete")'''
        output = compile_and_run(source)
        assert output.strip() == "... complete"
    
    def test_labeled_variables(self):
        """Print labeled variables pattern."""
        source = '''let name: str = "Alice"
let age: int = 30
let height: float = 1.65
print("Name:", name)
print("Age:", age)
print("Height:", height)'''
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines[0] == "Name: Alice"
        assert lines[1] == "Age: 30"
        assert lines[2] == "Height: 1.65"
    
    def test_key_value_pairs(self):
        """Print key-value pairs with sep."""
        source = '''print("x", "=", 10, sep="")
print("y", "=", 20, sep="")'''
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines[0] == "x=10"
        assert lines[1] == "y=20"
    
    def test_table_output(self):
        """Print table-like output."""
        source = '''print("ID", "Name", "Score", sep="\\t")
print(1, "Alice", 95, sep="\\t")
print(2, "Bob", 87, sep="\\t")'''
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines[0] == "ID\tName\tScore"
        assert lines[1] == "1\tAlice\t95"
        assert lines[2] == "2\tBob\t87"
    
    def test_countdown(self):
        """Countdown with inline output."""
        source = '''print(3, end=" ")
print(2, end=" ")
print(1, end=" ")
print("Go!")'''
        output = compile_and_run(source)
        assert output.strip() == "3 2 1 Go!"
    
    def test_mixed_output_complex(self):
        """Complex mixed output scenario."""
        source = '''let total: int = 0
let i: int = 1
while i <= 5 {
    total = total + i
    i = i + 1
}
print("Sum of 1 to 5 =", total)'''
        output = compile_and_run(source)
        assert output.strip() == "Sum of 1 to 5 = 15"


class TestEdgeCasesE2E:
    """E2E tests for edge cases."""
    
    def test_single_arg_with_sep(self):
        """Single arg with sep (sep ignored)."""
        output = compile_and_run('print(42, sep=",")')
        assert output.strip() == "42"
    
    def test_empty_string_output(self):
        """Print empty string."""
        output = compile_and_run('print("")')
        assert output == "\n"
    
    def test_string_with_spaces(self):
        """Print strings with spaces."""
        output = compile_and_run('print("hello world", "foo bar", sep=" | ")')
        assert output.strip() == "hello world | foo bar"
    
    def test_boolean_in_multiple_args(self):
        """Booleans in multiple args."""
        output = compile_and_run("print(true, false, true, sep=\" and \")")
        assert output.strip() == "True and False and True"

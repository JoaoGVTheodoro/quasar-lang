"""
Phase 7.2 Tests — Interactive Integration (E2E)

End-to-end tests for input() combined with type casting.
These tests validate complete interactive programs using mocked stdin.
"""

import pytest
import subprocess

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator


def compile_quasar(source: str) -> str:
    """Compile Quasar source to Python code."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    ast = SemanticAnalyzer().analyze(ast)
    return CodeGenerator().generate(ast)


def execute_python(code: str, stdin: str = "") -> str:
    """Execute Python code with optional stdin and capture output."""
    result = subprocess.run(
        ["python", "-c", code],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Python execution failed: {result.stderr}")
    return result.stdout


def compile_and_run(source: str, stdin: str = "") -> str:
    """Compile Quasar source and execute with optional stdin."""
    python_code = compile_quasar(source)
    return execute_python(python_code, stdin)


# =============================================================================
# Scenario 1: Simple Echo (String I/O)
# =============================================================================

class TestSimpleEcho:
    """Test basic input/output with strings."""
    
    def test_echo_with_prompt(self):
        """input() with prompt, print result."""
        source = '''
        let name: str = input("Name: ")
        print("Hello, {}", name)
        '''
        output = compile_and_run(source, "Alice\n")
        assert "Hello, Alice" in output
    
    def test_echo_no_prompt(self):
        """input() without prompt."""
        source = '''
        let name: str = input()
        print("Hello, {}", name)
        '''
        output = compile_and_run(source, "Bob\n")
        assert "Hello, Bob" in output
    
    def test_multiple_string_inputs(self):
        """Multiple input() calls."""
        source = '''
        let first: str = input()
        let last: str = input()
        print("{} {}", first, last)
        '''
        output = compile_and_run(source, "John\nDoe\n")
        assert "John Doe" in output


# =============================================================================
# Scenario 2: The Adder (Input + Cast + Math)
# =============================================================================

class TestIntegerArithmetic:
    """Test input with int casting and arithmetic."""
    
    def test_two_number_addition(self):
        """Add two integers from input."""
        source = '''
        let a: int = int(input())
        let b: int = int(input())
        print("Sum: {}", a + b)
        '''
        output = compile_and_run(source, "10\n20\n")
        assert "Sum: 30" in output
    
    def test_subtraction(self):
        """Subtract two integers from input."""
        source = '''
        let a: int = int(input())
        let b: int = int(input())
        print("Diff: {}", a - b)
        '''
        output = compile_and_run(source, "50\n30\n")
        assert "Diff: 20" in output
    
    def test_multiplication(self):
        """Multiply two integers from input."""
        source = '''
        let a: int = int(input())
        let b: int = int(input())
        print("Product: {}", a * b)
        '''
        output = compile_and_run(source, "7\n6\n")
        assert "Product: 42" in output
    
    def test_with_prompts(self):
        """Input with prompts for clarity."""
        source = '''
        let a: int = int(input("First: "))
        let b: int = int(input("Second: "))
        print("{} + {} = {}", a, b, a + b)
        '''
        output = compile_and_run(source, "15\n25\n")
        assert "15 + 25 = 40" in output


# =============================================================================
# Scenario 3: Circle Area (Float Math)
# =============================================================================

class TestFloatMath:
    """Test input with float casting and math."""
    
    def test_circle_area(self):
        """Calculate circle area from radius."""
        source = '''
        let r: float = float(input())
        let area: float = 3.14159 * r * r
        print("Area: {}", area)
        '''
        output = compile_and_run(source, "2\n")
        assert "Area: 12.56636" in output
    
    def test_rectangle_area(self):
        """Calculate rectangle area."""
        source = '''
        let w: float = float(input())
        let h: float = float(input())
        print("Area: {}", w * h)
        '''
        output = compile_and_run(source, "3.5\n2.0\n")
        assert "Area: 7.0" in output
    
    def test_temperature_conversion(self):
        """Celsius to Fahrenheit."""
        source = '''
        let c: float = float(input())
        let f: float = c * 1.8 + 32.0
        print("{}C = {}F", c, f)
        '''
        output = compile_and_run(source, "100\n")
        assert "100" in output
        assert "212" in output
    
    def test_average_calculation(self):
        """Calculate average of three numbers."""
        source = '''
        let a: float = float(input())
        let b: float = float(input())
        let c: float = float(input())
        let sum: float = a + b + c
        let avg: float = sum / 3.0
        print("Average: {}", avg)
        '''
        output = compile_and_run(source, "10\n20\n30\n")
        assert "Average: 20.0" in output


# =============================================================================
# Scenario 4: Age Checker (Logic + Bool)
# =============================================================================

class TestLogicAndBool:
    """Test input with boolean logic."""
    
    def test_adult_check(self):
        """Check if age >= 18."""
        source = '''
        let age: int = int(input())
        let is_adult: bool = age >= 18
        print("Adult: {}", is_adult)
        '''
        output = compile_and_run(source, "20\n")
        assert "Adult: True" in output
    
    def test_minor_check(self):
        """Check if age < 18."""
        source = '''
        let age: int = int(input())
        let is_adult: bool = age >= 18
        print("Adult: {}", is_adult)
        '''
        output = compile_and_run(source, "15\n")
        assert "Adult: False" in output
    
    def test_equality_check(self):
        """Check if two inputs are equal."""
        source = '''
        let a: int = int(input())
        let b: int = int(input())
        let equal: bool = a == b
        print("Equal: {}", equal)
        '''
        output = compile_and_run(source, "42\n42\n")
        assert "Equal: True" in output
    
    def test_range_check(self):
        """Check if value is in range."""
        source = '''
        let x: int = int(input())
        let in_range: bool = x >= 1 && x <= 10
        print("In range: {}", in_range)
        '''
        output = compile_and_run(source, "5\n")
        assert "In range: True" in output


# =============================================================================
# Scenario 5: Complex Programs
# =============================================================================

class TestComplexPrograms:
    """Test more complex interactive programs."""
    
    def test_simple_calculator(self):
        """A simple calculator with all operations."""
        source = '''
        let a: int = int(input())
        let b: int = int(input())
        print("{} + {} = {}", a, b, a + b)
        print("{} - {} = {}", a, b, a - b)
        print("{} * {} = {}", a, b, a * b)
        '''
        output = compile_and_run(source, "10\n3\n")
        assert "10 + 3 = 13" in output
        assert "10 - 3 = 7" in output
        assert "10 * 3 = 30" in output
    
    def test_conditional_greeting(self):
        """Greet based on time of day (hour)."""
        source = '''
        let hour: int = int(input())
        if hour < 12 {
            print("Good morning!")
        } else {
            print("Good afternoon!")
        }
        '''
        output = compile_and_run(source, "9\n")
        assert "Good morning!" in output
    
    def test_conditional_afternoon(self):
        """Greet afternoon."""
        source = '''
        let hour: int = int(input())
        if hour < 12 {
            print("Good morning!")
        } else {
            print("Good afternoon!")
        }
        '''
        output = compile_and_run(source, "15\n")
        assert "Good afternoon!" in output
    
    def test_loop_with_input_count(self):
        """Loop n times based on input."""
        source = '''
        let n: int = int(input())
        let sum: int = 0
        for i in 0..n {
            sum = sum + i
        }
        print("Sum 0..{}: {}", n, sum)
        '''
        output = compile_and_run(source, "5\n")
        assert "Sum 0..5: 10" in output
    
    def test_chained_casting(self):
        """Chain multiple type conversions."""
        source = '''
        let input_str: str = input()
        let as_float: float = float(input_str)
        let as_int: int = int(as_float)
        let back_to_str: str = str(as_int)
        print("Result: {}", back_to_str)
        '''
        output = compile_and_run(source, "3.99\n")
        assert "Result: 3" in output


# =============================================================================
# Scenario 6: Function Integration
# =============================================================================

class TestFunctionIntegration:
    """Test input with user-defined functions."""
    
    def test_function_with_input(self):
        """Pass input value to function."""
        source = '''
        fn double(x: int) -> int {
            return x * 2
        }
        
        let n: int = int(input())
        print("Double: {}", double(n))
        '''
        output = compile_and_run(source, "21\n")
        assert "Double: 42" in output
    
    def test_multiple_function_calls(self):
        """Multiple functions with input."""
        source = '''
        fn square(x: int) -> int {
            return x * x
        }
        
        fn cube(x: int) -> int {
            return x * x * x
        }
        
        let n: int = int(input())
        print("Square: {}", square(n))
        print("Cube: {}", cube(n))
        '''
        output = compile_and_run(source, "3\n")
        assert "Square: 9" in output
        assert "Cube: 27" in output
    
    def test_function_with_multiple_inputs(self):
        """Function with multiple input values."""
        source = '''
        fn add(a: int, b: int) -> int {
            return a + b
        }
        
        let x: int = int(input())
        let y: int = int(input())
        print("Result: {}", add(x, y))
        '''
        output = compile_and_run(source, "100\n200\n")
        assert "Result: 300" in output


# =============================================================================
# Scenario 7: List Operations with Input
# =============================================================================

class TestListWithInput:
    """Test input with list operations."""
    
    def test_list_size_from_input(self):
        """Use input to determine iterations."""
        source = '''
        let n: int = int(input())
        let nums: [int] = []
        for i in 0..n {
            push(nums, i * i)
        }
        print("Length: {}", len(nums))
        '''
        output = compile_and_run(source, "5\n")
        assert "Length: 5" in output
    
    def test_accumulate_in_loop(self):
        """Accumulate values based on input count."""
        source = '''
        let count: int = int(input())
        let total: int = 0
        for i in 1..count + 1 {
            total = total + i
        }
        print("Total: {}", total)
        '''
        output = compile_and_run(source, "10\n")
        # 1+2+3+4+5+6+7+8+9+10 = 55
        assert "Total: 55" in output

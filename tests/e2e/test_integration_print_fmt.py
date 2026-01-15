"""
End-to-end integration tests for print formatting (Phase 5.2).

These tests verify the complete pipeline for:
- Format string with {} placeholders
- .format() invocation at runtime
- Escape sequences {{ and }}
- Normal mode preservation (variable as first arg)
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


# =============================================================================
# Case 1: Basic Formatting
# =============================================================================

class TestBasicFormatting:
    """Basic format string tests."""
    
    def test_format_single_int(self):
        """print('Value: {}', 42) -> 'Value: 42'"""
        output = compile_and_run('print("Value: {}", 42)')
        assert output.strip() == "Value: 42"
    
    def test_format_single_string(self):
        """print('Hello, {}!', 'World') -> 'Hello, World!'"""
        output = compile_and_run('print("Hello, {}!", "World")')
        assert output.strip() == "Hello, World!"
    
    def test_format_single_float(self):
        """print('Pi: {}', 3.14) -> 'Pi: 3.14'"""
        output = compile_and_run('print("Pi: {}", 3.14)')
        assert output.strip() == "Pi: 3.14"
    
    def test_format_single_bool_true(self):
        """print('Active: {}', true) -> 'Active: True'"""
        output = compile_and_run('print("Active: {}", true)')
        assert output.strip() == "Active: True"
    
    def test_format_single_bool_false(self):
        """print('Active: {}', false) -> 'Active: False'"""
        output = compile_and_run('print("Active: {}", false)')
        assert output.strip() == "Active: False"
    
    def test_format_with_variable(self):
        """Format with variable argument."""
        source = 'let x: int = 100\nprint("X = {}", x)'
        output = compile_and_run(source)
        assert output.strip() == "X = 100"


# =============================================================================
# Case 2: Multiple Placeholders
# =============================================================================

class TestMultiplePlaceholders:
    """Tests for multiple {} placeholders."""
    
    def test_format_two_placeholders(self):
        """print('{} + {} = 30', 10, 20) -> '10 + 20 = 30'"""
        output = compile_and_run('print("{} + {} = 30", 10, 20)')
        assert output.strip() == "10 + 20 = 30"
    
    def test_format_three_placeholders(self):
        """print('{} + {} = {}', 10, 20, 30) -> '10 + 20 = 30'"""
        output = compile_and_run('print("{} + {} = {}", 10, 20, 30)')
        assert output.strip() == "10 + 20 = 30"
    
    def test_format_four_placeholders(self):
        """print('{}, {}, {}, {}', 1, 2, 3, 4) -> '1, 2, 3, 4'"""
        output = compile_and_run('print("{}, {}, {}, {}", 1, 2, 3, 4)')
        assert output.strip() == "1, 2, 3, 4"
    
    def test_format_mixed_types(self):
        """print('Name: {}, Age: {}, Active: {}', 'Alice', 30, true)"""
        output = compile_and_run('print("Name: {}, Age: {}, Active: {}", "Alice", 30, true)')
        assert output.strip() == "Name: Alice, Age: 30, Active: True"
    
    def test_format_with_expressions(self):
        """print('Sum: {}, Product: {}', 2+3, 4*5)"""
        output = compile_and_run('print("Sum: {}, Product: {}", 2 + 3, 4 * 5)')
        assert output.strip() == "Sum: 5, Product: 20"
    
    def test_format_coordinates(self):
        """print('Point({}, {})', x, y)"""
        source = 'let x: int = 10\nlet y: int = 20\nprint("Point({}, {})", x, y)'
        output = compile_and_run(source)
        assert output.strip() == "Point(10, 20)"


# =============================================================================
# Case 3: Formatting with end Parameter
# =============================================================================

class TestFormattingWithEnd:
    """Tests for format strings with end parameter."""
    
    def test_format_with_end_percent(self):
        """print('Loading: {}', 99, end='%') -> 'Loading: 99%'"""
        # Note: no newline at end
        output = compile_and_run('print("Loading: {}", 99, end="%")')
        assert output == "Loading: 99%"  # No strip, check exact
    
    def test_format_with_end_empty(self):
        """print('Test: {}', 1, end='') -> 'Test: 1' (no newline)"""
        output = compile_and_run('print("Test: {}", 1, end="")')
        assert output == "Test: 1"
    
    def test_format_with_end_exclamation(self):
        """print('Done: {}', 'OK', end='!') -> 'Done: OK!'"""
        output = compile_and_run('print("Done: {}", "OK", end="!")')
        assert output == "Done: OK!"
    
    def test_format_multi_with_end(self):
        """Multiple placeholders with end."""
        output = compile_and_run('print("{} x {} = {}", 3, 4, 12, end="\\n\\n")')
        assert output == "3 x 4 = 12\n\n"
    
    def test_format_progress_bar_simulation(self):
        """Simulate progress output."""
        source = '''print("Progress: {}", 50, end="%")
print(" complete", end="!")'''
        output = compile_and_run(source)
        assert output == "Progress: 50% complete!"


# =============================================================================
# Case 4: Escape Sequences (CRITICAL)
# =============================================================================

class TestEscapeSequences:
    """Tests for {{ and }} escape sequences."""
    
    def test_escape_no_args_literal(self):
        """print('Use {{}} for placeholders') -> 'Use {{}} for placeholders'
        
        Note: Single arg = normal mode. The string is printed as-is.
        Python's print doesn't process {{ }} escapes.
        """
        output = compile_and_run('print("Use {{}} for placeholders")')
        assert output.strip() == "Use {{}} for placeholders"
    
    def test_escape_with_format(self):
        """print('The set is {{ {} }}', 42) -> 'The set is { 42 }'
        
        Format mode: .format() processes {{ -> { and {} -> argument.
        """
        output = compile_and_run('print("The set is {{ {} }}", 42)')
        assert output.strip() == "The set is { 42 }"
    
    def test_escape_multiple_braces_no_format(self):
        """print('{{}}{{}}') -> '{{}}{{}}' (single arg, no format)"""
        output = compile_and_run('print("{{}}{{}}")')
        assert output.strip() == "{{}}{{}}"
    
    def test_escape_mixed_complex(self):
        """print('A={{}} B={}', 42) -> 'A={} B=42'
        
        Format mode: {{ -> {, {} -> 42
        """
        output = compile_and_run('print("A={{}} B={}", 42)')
        assert output.strip() == "A={} B=42"
    
    def test_escape_surrounding_text(self):
        """print('Start {{{}}} End', 'middle') -> 'Start {middle} End'"""
        output = compile_and_run('print("Start {{{}}} End", "middle")')
        assert output.strip() == "Start {middle} End"
    
    def test_escape_json_dict_style(self):
        """Format with JSON-like structure using escapes."""
        # Quasar: print("{{key: {}}}", "value")
        # Python: print("{{key: {}}}".format("value")) -> "{key: value}"
        output = compile_and_run('print("{{key: {}}}", "value")')
        assert output.strip() == "{key: value}"


# =============================================================================
# Case 5: The "No Magic" Check (Regression)
# =============================================================================

class TestNoMagicRegression:
    """Ensure variable-first-arg is treated as normal print."""
    
    def test_variable_format_string_not_formatted(self):
        """let fmt='Val: {}'; print(fmt, 10) -> 'Val: {} 10'"""
        source = 'let fmt: str = "Val: {}"\nprint(fmt, 10)'
        output = compile_and_run(source)
        # Normal mode: two args printed with space separator
        assert output.strip() == "Val: {} 10"
    
    def test_variable_no_placeholder_multi_args(self):
        """let s='hello'; print(s, 'world') -> 'hello world'"""
        source = 'let s: str = "hello"\nprint(s, "world")'
        output = compile_and_run(source)
        assert output.strip() == "hello world"
    
    def test_literal_no_placeholder_multi_args(self):
        """print('hello', 1, 2) -> 'hello 1 2' (no {} = normal mode)"""
        output = compile_and_run('print("hello", 1, 2)')
        assert output.strip() == "hello 1 2"
    
    def test_only_escaped_not_formatted(self):
        """print('{{}}', 1) -> '{{}} 1' (escaped = no real placeholder = normal mode)
        
        Normal mode: string printed as-is, no .format() processing.
        """
        output = compile_and_run('print("{{}}", 1)')
        assert output.strip() == "{{}} 1"
    
    def test_single_arg_placeholder_literal(self):
        """print('{}') -> '{}' (single arg = no formatting)"""
        output = compile_and_run('print("{}")')
        assert output.strip() == "{}"


# =============================================================================
# Real-World Scenarios
# =============================================================================

class TestRealWorldScenarios:
    """Practical use cases for formatted output."""
    
    def test_error_message_formatting(self):
        """Error message with code and description."""
        source = '''let code: int = 404
let msg: str = "Not Found"
print("Error {}: {}", code, msg)'''
        output = compile_and_run(source)
        assert output.strip() == "Error 404: Not Found"
    
    def test_table_row_formatting(self):
        """Format a simple table row."""
        source = '''print("| {} | {} | {} |", "Name", "Age", "City")
print("| {} | {} | {} |", "Alice", 30, "NYC")'''
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines[0] == "| Name | Age | City |"
        assert lines[1] == "| Alice | 30 | NYC |"
    
    def test_countdown_formatting(self):
        """Countdown with formatting."""
        source = '''let i: int = 3
while i > 0 {
    print("T-{}", i)
    i = i - 1
}
print("Liftoff!")'''
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines == ["T-3", "T-2", "T-1", "Liftoff!"]
    
    def test_function_result_formatting(self):
        """Format function return value."""
        source = '''fn square(n: int) -> int {
    return n * n
}
print("5 squared is {}", square(5))'''
        output = compile_and_run(source)
        assert output.strip() == "5 squared is 25"
    
    def test_conditional_message(self):
        """Conditional message with formatting."""
        source = '''let score: int = 85
if score >= 70 {
    print("You passed with {}%!", score)
} else {
    print("Score: {}%. Try again.", score)
}'''
        output = compile_and_run(source)
        assert output.strip() == "You passed with 85%!"
    
    def test_accumulator_display(self):
        """Display accumulator in loop."""
        source = '''let sum: int = 0
let i: int = 1
while i <= 3 {
    sum = sum + i
    print("After adding {}: sum = {}", i, sum)
    i = i + 1
}'''
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines[0] == "After adding 1: sum = 1"
        assert lines[1] == "After adding 2: sum = 3"
        assert lines[2] == "After adding 3: sum = 6"


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================

class TestEdgeCases:
    """Edge cases and boundary conditions."""
    
    def test_empty_string_format_arg(self):
        """print('Value: {}', '') -> 'Value: '"""
        output = compile_and_run('print("Value: {}", "")')
        assert output.strip() == "Value:"
    
    def test_placeholder_at_start(self):
        """print('{} is first', 'This') -> 'This is first'"""
        output = compile_and_run('print("{} is first", "This")')
        assert output.strip() == "This is first"
    
    def test_placeholder_at_end(self):
        """print('Last is {}', 'here') -> 'Last is here'"""
        output = compile_and_run('print("Last is {}", "here")')
        assert output.strip() == "Last is here"
    
    def test_consecutive_placeholders(self):
        """print('{}{}{}', 'A', 'B', 'C') -> 'ABC'"""
        output = compile_and_run('print("{}{}{}", "A", "B", "C")')
        assert output.strip() == "ABC"
    
    def test_placeholder_only(self):
        """print('{}', 42) -> '42'"""
        output = compile_and_run('print("{}", 42)')
        assert output.strip() == "42"
    
    def test_negative_number_formatting(self):
        """print('Temp: {}C', -5) -> 'Temp: -5C'"""
        output = compile_and_run('print("Temp: {}C", 0 - 5)')
        assert output.strip() == "Temp: -5C"
    
    def test_zero_value_formatting(self):
        """print('Count: {}', 0) -> 'Count: 0'"""
        output = compile_and_run('print("Count: {}", 0)')
        assert output.strip() == "Count: 0"
    
    def test_large_number_formatting(self):
        """print('Big: {}', 999999) -> 'Big: 999999'"""
        output = compile_and_run('print("Big: {}", 999999)')
        assert output.strip() == "Big: 999999"

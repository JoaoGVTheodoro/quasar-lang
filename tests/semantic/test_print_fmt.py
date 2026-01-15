"""
Tests for print format string validation (Phase 5.2).
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.semantic.errors import SemanticError


def analyze(source: str):
    """Helper to analyze source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast)


class TestFormatStringValidation:
    """Tests for format string placeholder validation (Phase 5.2)."""
    
    def test_fmt_valid_single(self):
        """print('{}', 1) should be valid."""
        # Should not raise
        analyze('print("{}", 1)')
    
    def test_fmt_valid_multi(self):
        """print('{} {}', 1, 2) should be valid."""
        # Should not raise
        analyze('print("{} {}", 1, 2)')
    
    def test_fmt_valid_three_placeholders(self):
        """print('{}, {}, {}', a, b, c) should be valid."""
        analyze('print("{}, {}, {}", 1, 2, 3)')
    
    def test_fmt_valid_with_text(self):
        """print('X={}, Y={}', x, y) should be valid."""
        analyze('let x: int = 10\nlet y: int = 20\nprint("X={}, Y={}", x, y)')
    
    def test_fmt_valid_mixed_types(self):
        """Format with mixed types should be valid."""
        analyze('print("Name: {}, Age: {}, Active: {}", "Alice", 30, true)')
    
    def test_fmt_error_too_few_E0410(self):
        """print('{} {}', 1) should raise E0410 (too few args)."""
        with pytest.raises(SemanticError) as exc_info:
            analyze('print("{} {}", 1)')
        
        assert exc_info.value.code == "E0410"
        assert "2" in str(exc_info.value)  # Expected 2 placeholders
        assert "1" in str(exc_info.value)  # Got 1 argument
    
    def test_fmt_error_too_few_three_vs_one(self):
        """print('{} {} {}', 1) should raise E0410."""
        with pytest.raises(SemanticError) as exc_info:
            analyze('print("{} {} {}", 1)')
        
        assert exc_info.value.code == "E0410"
    
    def test_fmt_error_too_many_E0411(self):
        """print('{}', 1, 2) should raise E0411 (too many args)."""
        with pytest.raises(SemanticError) as exc_info:
            analyze('print("{}", 1, 2)')
        
        assert exc_info.value.code == "E0411"
        assert "1" in str(exc_info.value)  # Expected 1 placeholder
        assert "2" in str(exc_info.value)  # Got 2 arguments
    
    def test_fmt_error_too_many_one_vs_four(self):
        """print('{}', 1, 2, 3, 4) should raise E0411."""
        with pytest.raises(SemanticError) as exc_info:
            analyze('print("{}", 1, 2, 3, 4)')
        
        assert exc_info.value.code == "E0411"


class TestFormatStringEdgeCases:
    """Edge cases for format string handling."""
    
    def test_fmt_ignore_single_arg_literal(self):
        """print('{}') single arg should print literal, no error."""
        # No formatting when only format string with no args
        analyze('print("{}")')
    
    def test_fmt_ignore_variable_format_string(self):
        """print(f, 1) where f is variable should NOT format."""
        # Variable as first arg = normal mode, not format mode
        analyze('let f: str = "{}"\nprint(f, 1)')
    
    def test_fmt_escaped_braces_not_counted(self):
        """print('{{}}', 1) - escaped braces = 0 placeholders = normal mode."""
        # {{}} is escaped (0 real placeholders), so this is normal mode, not format mode
        # Normal mode accepts any number of args, so this should pass
        analyze('print("{{}}", 1)')
    
    def test_fmt_mixed_escaped_and_real(self):
        """print('{{}} {}', 1) should be valid (1 real placeholder)."""
        analyze('print("{{}} {}", 1)')
    
    def test_fmt_multiple_escaped(self):
        """print('{{}}{{}}') should be valid (no placeholders)."""
        analyze('print("{{}}{{}}")')
    
    def test_fmt_with_end_parameter(self):
        """print('{}', 1, end='!') should be valid."""
        analyze('print("{}", 1, end="!")')
    
    def test_fmt_with_sep_parameter(self):
        """Format string with sep should still validate placeholders."""
        analyze('print("{}", 1, sep=",")')
    
    def test_fmt_no_placeholder_multi_args(self):
        """print('hello', 1, 2) - no placeholder, normal mode."""
        # No {} in first arg = normal mode, all args valid
        analyze('print("hello", 1, 2)')
    
    def test_fmt_empty_string_multi_args(self):
        """print('', 1) - empty string, no placeholder, normal mode."""
        analyze('print("", 1)')


class TestFormatStringTypes:
    """Type validation within format strings."""
    
    def test_fmt_with_int(self):
        """Format with int arg should be valid."""
        analyze('print("Value: {}", 42)')
    
    def test_fmt_with_float(self):
        """Format with float arg should be valid."""
        analyze('print("Pi: {}", 3.14)')
    
    def test_fmt_with_bool_true(self):
        """Format with bool true should be valid."""
        analyze('print("Active: {}", true)')
    
    def test_fmt_with_bool_false(self):
        """Format with bool false should be valid."""
        analyze('print("Active: {}", false)')
    
    def test_fmt_with_string(self):
        """Format with string arg should be valid."""
        analyze('print("Name: {}", "Alice")')
    
    def test_fmt_with_expression(self):
        """Format with expression arg should be valid."""
        analyze('print("Sum: {}", 1 + 2)')
    
    def test_fmt_with_variable(self):
        """Format with variable arg should be valid."""
        analyze('let x: int = 42\nprint("X: {}", x)')
    
    def test_fmt_with_function_call(self):
        """Format with function call arg should be valid."""
        source = """fn double(n: int) -> int {
    return n * 2
}
print("Result: {}", double(5))"""
        analyze(source)

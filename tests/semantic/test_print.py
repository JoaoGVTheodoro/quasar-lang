"""
Tests for print statement semantic analysis (Phase 5 + 5.1).
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


class TestPrintStatementSemantic:
    """Tests for print statement semantic validation."""
    
    def test_print_int_valid(self):
        """print(int) should be valid."""
        # Should not raise
        analyze("print(42)")
    
    def test_print_float_valid(self):
        """print(float) should be valid."""
        # Should not raise
        analyze("print(3.14)")
    
    def test_print_bool_valid(self):
        """print(bool) should be valid."""
        # Should not raise
        analyze("print(true)")
        analyze("print(false)")
    
    def test_print_str_valid(self):
        """print(str) should be valid."""
        # Should not raise
        analyze('print("hello")')
    
    def test_print_expression_valid(self):
        """print with complex expressions should be valid."""
        # Should not raise
        analyze("print(2 + 3)")
        analyze("print(10 > 5)")
        analyze('print("hello" + " world")')
    
    def test_print_variable_valid(self):
        """print with declared variable should be valid."""
        # Should not raise
        analyze("let x: int = 42\nprint(x)")
    
    def test_print_undefined_variable_error(self):
        """print with undefined variable should raise E0001."""
        with pytest.raises(SemanticError) as exc_info:
            analyze("print(undefined_var)")
        
        assert exc_info.value.code == "E0001"
        assert "undeclared" in str(exc_info.value)
    
    def test_print_type_error_in_expression(self):
        """print with type error in expression should raise E0102."""
        with pytest.raises(SemanticError) as exc_info:
            analyze('print(1 + "hello")')
        
        # E0102: operator not supported for types
        assert exc_info.value.code == "E0102"


class TestPrintMultipleArgumentsSemantic:
    """Tests for print with multiple arguments (Phase 5.1)."""
    
    def test_print_multiple_ints_valid(self):
        """print(1, 2, 3) should be valid."""
        analyze("print(1, 2, 3)")
    
    def test_print_multiple_mixed_types_valid(self):
        """print with mixed primitive types should be valid."""
        analyze('print("Name:", 42, true, 3.14)')
    
    def test_print_multiple_variables_valid(self):
        """print with multiple declared variables should be valid."""
        analyze("""let a: int = 1
let b: str = "hello"
let c: bool = true
print(a, b, c)""")
    
    def test_print_multiple_with_expressions_valid(self):
        """print with expressions in multiple args should be valid."""
        analyze("print(1 + 2, 3 * 4, 5 > 0)")
    
    def test_print_multiple_undefined_variable_error(self):
        """print with undefined variable in args should raise E0001."""
        with pytest.raises(SemanticError) as exc_info:
            analyze("print(1, undefined, 3)")
        
        assert exc_info.value.code == "E0001"
    
    def test_print_multiple_type_error_in_expression(self):
        """print with type error in any arg should raise E0102."""
        with pytest.raises(SemanticError) as exc_info:
            analyze('print(1, 2 + "x", 3)')
        
        assert exc_info.value.code == "E0102"


class TestPrintSepEndSemantic:
    """Tests for print sep/end parameters (Phase 5.1)."""
    
    def test_print_sep_string_literal_valid(self):
        """print with sep as string literal should be valid."""
        analyze('print(1, 2, sep=", ")')
    
    def test_print_end_string_literal_valid(self):
        """print with end as string literal should be valid."""
        analyze('print(1, end="")')
    
    def test_print_sep_and_end_valid(self):
        """print with both sep and end should be valid."""
        analyze('print(1, 2, sep="-", end="!")')
    
    def test_print_sep_variable_valid(self):
        """print with sep as string variable should be valid."""
        analyze('let s: str = ","\nprint(1, 2, sep=s)')
    
    def test_print_end_variable_valid(self):
        """print with end as string variable should be valid."""
        analyze('let e: str = ""\nprint(1, end=e)')
    
    def test_print_sep_int_error_E0402(self):
        """print with sep as int should raise E0402."""
        with pytest.raises(SemanticError) as exc_info:
            analyze("print(1, 2, sep=42)")
        
        assert exc_info.value.code == "E0402"
        assert "'sep'" in str(exc_info.value)
        assert "'str'" in str(exc_info.value)
        assert "'int'" in str(exc_info.value)
    
    def test_print_sep_bool_error_E0402(self):
        """print with sep as bool should raise E0402."""
        with pytest.raises(SemanticError) as exc_info:
            analyze("print(1, 2, sep=true)")
        
        assert exc_info.value.code == "E0402"
    
    def test_print_sep_float_error_E0402(self):
        """print with sep as float should raise E0402."""
        with pytest.raises(SemanticError) as exc_info:
            analyze("print(1, 2, sep=3.14)")
        
        assert exc_info.value.code == "E0402"
    
    def test_print_end_int_error_E0403(self):
        """print with end as int should raise E0403."""
        with pytest.raises(SemanticError) as exc_info:
            analyze("print(1, end=0)")
        
        assert exc_info.value.code == "E0403"
        assert "'end'" in str(exc_info.value)
        assert "'str'" in str(exc_info.value)
        assert "'int'" in str(exc_info.value)
    
    def test_print_end_bool_error_E0403(self):
        """print with end as bool should raise E0403."""
        with pytest.raises(SemanticError) as exc_info:
            analyze("print(1, end=false)")
        
        assert exc_info.value.code == "E0403"
    
    def test_print_end_float_error_E0403(self):
        """print with end as float should raise E0403."""
        with pytest.raises(SemanticError) as exc_info:
            analyze("print(1, end=1.0)")
        
        assert exc_info.value.code == "E0403"
    
    def test_print_sep_undefined_variable_error(self):
        """print with undefined sep variable should raise E0001."""
        with pytest.raises(SemanticError) as exc_info:
            analyze("print(1, sep=undefined_sep)")
        
        assert exc_info.value.code == "E0001"
    
    def test_print_end_undefined_variable_error(self):
        """print with undefined end variable should raise E0001."""
        with pytest.raises(SemanticError) as exc_info:
            analyze("print(1, end=undefined_end)")
        
        assert exc_info.value.code == "E0001"

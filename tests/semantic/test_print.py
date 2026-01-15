"""
Tests for print statement semantic analysis (Phase 5).
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

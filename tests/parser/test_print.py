"""
Tests for print statement parsing (Phase 5).
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.parser.errors import ParserError
from quasar.ast import (
    PrintStmt,
    IntLiteral,
    FloatLiteral,
    StringLiteral,
    BoolLiteral,
    Identifier,
    BinaryExpr,
    CallExpr,
)


def parse(source: str):
    """Helper to parse source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


class TestPrintStatementParsing:
    """Tests for print statement parsing."""
    
    def test_parse_print_int_literal(self):
        """Should parse print(42)."""
        ast = parse("print(42)")
        
        assert len(ast.declarations) == 1
        stmt = ast.declarations[0]
        assert isinstance(stmt, PrintStmt)
        assert isinstance(stmt.expression, IntLiteral)
        assert stmt.expression.value == 42
    
    def test_parse_print_string_literal(self):
        """Should parse print(\"hello\")."""
        ast = parse('print("hello")')
        
        stmt = ast.declarations[0]
        assert isinstance(stmt, PrintStmt)
        assert isinstance(stmt.expression, StringLiteral)
        assert stmt.expression.value == "hello"
    
    def test_parse_print_variable(self):
        """Should parse print(x) with variable reference."""
        ast = parse("let x: int = 5\nprint(x)")
        
        assert len(ast.declarations) == 2
        stmt = ast.declarations[1]
        assert isinstance(stmt, PrintStmt)
        assert isinstance(stmt.expression, Identifier)
        assert stmt.expression.name == "x"
    
    def test_parse_print_binary_expression(self):
        """Should parse print(2 + 3)."""
        ast = parse("print(2 + 3)")
        
        stmt = ast.declarations[0]
        assert isinstance(stmt, PrintStmt)
        assert isinstance(stmt.expression, BinaryExpr)
    
    def test_parse_print_function_call(self):
        """Should parse print(f(x))."""
        source = """fn double(n: int) -> int {
    return n * 2
}
print(double(5))"""
        ast = parse(source)
        
        assert len(ast.declarations) == 2
        stmt = ast.declarations[1]
        assert isinstance(stmt, PrintStmt)
        assert isinstance(stmt.expression, CallExpr)
        assert stmt.expression.callee == "double"
    
    def test_parse_print_missing_paren_error(self):
        """Should error on print 42 (missing parens)."""
        with pytest.raises(ParserError) as exc_info:
            parse("print 42")
        
        assert "'('" in str(exc_info.value)

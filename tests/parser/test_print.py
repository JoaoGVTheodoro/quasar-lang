"""
Tests for print statement parsing (Phase 5 + 5.1).
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
        assert len(stmt.arguments) == 1
        assert isinstance(stmt.arguments[0], IntLiteral)
        assert stmt.arguments[0].value == 42
        assert stmt.sep is None
        assert stmt.end is None
    
    def test_parse_print_string_literal(self):
        """Should parse print(\"hello\")."""
        ast = parse('print("hello")')
        
        stmt = ast.declarations[0]
        assert isinstance(stmt, PrintStmt)
        assert len(stmt.arguments) == 1
        assert isinstance(stmt.arguments[0], StringLiteral)
        assert stmt.arguments[0].value == "hello"
    
    def test_parse_print_variable(self):
        """Should parse print(x) with variable reference."""
        ast = parse("let x: int = 5\nprint(x)")
        
        assert len(ast.declarations) == 2
        stmt = ast.declarations[1]
        assert isinstance(stmt, PrintStmt)
        assert len(stmt.arguments) == 1
        assert isinstance(stmt.arguments[0], Identifier)
        assert stmt.arguments[0].name == "x"
    
    def test_parse_print_binary_expression(self):
        """Should parse print(2 + 3)."""
        ast = parse("print(2 + 3)")
        
        stmt = ast.declarations[0]
        assert isinstance(stmt, PrintStmt)
        assert len(stmt.arguments) == 1
        assert isinstance(stmt.arguments[0], BinaryExpr)
    
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
        assert len(stmt.arguments) == 1
        assert isinstance(stmt.arguments[0], CallExpr)
        assert stmt.arguments[0].callee == "double"
    
    def test_parse_print_missing_paren_error(self):
        """Should error on print 42 (missing parens)."""
        with pytest.raises(ParserError) as exc_info:
            parse("print 42")
        
        assert "'('" in str(exc_info.value)


class TestPrintMultipleArguments:
    """Tests for print with multiple arguments (Phase 5.1)."""
    
    def test_parse_print_two_arguments(self):
        """Should parse print(a, b)."""
        ast = parse("let a: int = 1\nlet b: int = 2\nprint(a, b)")
        
        stmt = ast.declarations[2]
        assert isinstance(stmt, PrintStmt)
        assert len(stmt.arguments) == 2
        assert isinstance(stmt.arguments[0], Identifier)
        assert stmt.arguments[0].name == "a"
        assert isinstance(stmt.arguments[1], Identifier)
        assert stmt.arguments[1].name == "b"
    
    def test_parse_print_three_arguments(self):
        """Should parse print(1, 2, 3)."""
        ast = parse("print(1, 2, 3)")
        
        stmt = ast.declarations[0]
        assert isinstance(stmt, PrintStmt)
        assert len(stmt.arguments) == 3
        assert all(isinstance(arg, IntLiteral) for arg in stmt.arguments)
        assert [arg.value for arg in stmt.arguments] == [1, 2, 3]
    
    def test_parse_print_mixed_types(self):
        """Should parse print with mixed argument types."""
        ast = parse('print("Name:", 42, true)')
        
        stmt = ast.declarations[0]
        assert len(stmt.arguments) == 3
        assert isinstance(stmt.arguments[0], StringLiteral)
        assert isinstance(stmt.arguments[1], IntLiteral)
        assert isinstance(stmt.arguments[2], BoolLiteral)
    
    def test_parse_print_expressions(self):
        """Should parse print with complex expressions."""
        ast = parse("print(1 + 2, 3 * 4)")
        
        stmt = ast.declarations[0]
        assert len(stmt.arguments) == 2
        assert all(isinstance(arg, BinaryExpr) for arg in stmt.arguments)


class TestPrintSepEnd:
    """Tests for print with sep and end parameters (Phase 5.1)."""
    
    def test_parse_print_with_sep(self):
        """Should parse print(a, b, sep=',')."""
        ast = parse('print(1, 2, sep=",")')
        
        stmt = ast.declarations[0]
        assert isinstance(stmt, PrintStmt)
        assert len(stmt.arguments) == 2
        assert stmt.sep is not None
        assert isinstance(stmt.sep, StringLiteral)
        assert stmt.sep.value == ","
        assert stmt.end is None
    
    def test_parse_print_with_end(self):
        """Should parse print(a, end='')."""
        ast = parse('print(1, end="")')
        
        stmt = ast.declarations[0]
        assert len(stmt.arguments) == 1
        assert stmt.sep is None
        assert stmt.end is not None
        assert isinstance(stmt.end, StringLiteral)
        assert stmt.end.value == ""
    
    def test_parse_print_with_sep_and_end(self):
        """Should parse print(a, b, sep='-', end='!')."""
        ast = parse('print(1, 2, sep="-", end="!")')
        
        stmt = ast.declarations[0]
        assert len(stmt.arguments) == 2
        assert stmt.sep is not None
        assert stmt.sep.value == "-"
        assert stmt.end is not None
        assert stmt.end.value == "!"
    
    def test_parse_print_end_before_sep(self):
        """Should parse print(a, end='!', sep=',') - order flexible."""
        ast = parse('print(1, end="!", sep=",")')
        
        stmt = ast.declarations[0]
        assert stmt.sep is not None
        assert stmt.sep.value == ","
        assert stmt.end is not None
        assert stmt.end.value == "!"
    
    def test_parse_print_sep_with_variable(self):
        """Should parse print(a, b, sep=s) with variable sep."""
        ast = parse('let s: str = ","\nprint(1, 2, sep=s)')
        
        stmt = ast.declarations[1]
        assert stmt.sep is not None
        assert isinstance(stmt.sep, Identifier)
        assert stmt.sep.name == "s"
    
    def test_parse_print_many_args_with_sep_end(self):
        """Should parse print with many args and both sep/end."""
        ast = parse('print(1, 2, 3, 4, 5, sep=", ", end="\\n\\n")')
        
        stmt = ast.declarations[0]
        assert len(stmt.arguments) == 5
        assert stmt.sep is not None
        assert stmt.end is not None
    
    def test_parse_print_single_arg_with_end(self):
        """Should parse print(x, end='') - single arg with end."""
        ast = parse('print(42, end="")')
        
        stmt = ast.declarations[0]
        assert len(stmt.arguments) == 1
        assert stmt.arguments[0].value == 42
        assert stmt.end is not None
        assert stmt.end.value == ""
    
    def test_parse_print_labeled_output(self):
        """Should parse print('Label:', value) pattern."""
        ast = parse('let x: int = 42\nprint("x =", x)')
        
        stmt = ast.declarations[1]
        assert len(stmt.arguments) == 2
        assert isinstance(stmt.arguments[0], StringLiteral)
        assert stmt.arguments[0].value == "x ="
        assert isinstance(stmt.arguments[1], Identifier)

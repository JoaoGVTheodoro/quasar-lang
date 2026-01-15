"""
Parser tests — Expression parsing.

Tests that expressions produce correct AST nodes with proper precedence.
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.ast import (
    FnDecl,
    ReturnStmt,
    BinaryExpr,
    UnaryExpr,
    CallExpr,
    Identifier,
    IntLiteral,
    FloatLiteral,
    StringLiteral,
    BoolLiteral,
    BinaryOp,
    UnaryOp,
)


def parse_expr(expr_source: str):
    """Helper to parse an expression (via return statement)."""
    source = f"fn test() -> int {{ return {expr_source} }}"
    lexer = Lexer(source, "test.qsr")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    prog = parser.parse()
    fn = prog.declarations[0]
    ret = fn.body.declarations[0]
    assert isinstance(ret, ReturnStmt)
    return ret.value


class TestLiterals:
    """Test literal expression parsing."""
    
    def test_int_literal(self) -> None:
        """Integer literals should produce IntLiteral."""
        expr = parse_expr("42")
        assert isinstance(expr, IntLiteral)
        assert expr.value == 42
    
    def test_float_literal(self) -> None:
        """Float literals should produce FloatLiteral."""
        expr = parse_expr("3.14")
        assert isinstance(expr, FloatLiteral)
        assert expr.value == 3.14
    
    def test_string_literal(self) -> None:
        """String literals should produce StringLiteral."""
        expr = parse_expr('"hello"')
        assert isinstance(expr, StringLiteral)
        assert expr.value == "hello"
    
    def test_bool_literal_true(self) -> None:
        """true should produce BoolLiteral with True."""
        expr = parse_expr("true")
        assert isinstance(expr, BoolLiteral)
        assert expr.value is True
    
    def test_bool_literal_false(self) -> None:
        """false should produce BoolLiteral with False."""
        expr = parse_expr("false")
        assert isinstance(expr, BoolLiteral)
        assert expr.value is False


class TestIdentifier:
    """Test identifier expression parsing."""
    
    def test_simple_identifier(self) -> None:
        """Identifier should produce Identifier node."""
        expr = parse_expr("myVar")
        assert isinstance(expr, Identifier)
        assert expr.name == "myVar"


class TestArithmeticOperators:
    """Test arithmetic operator parsing."""
    
    @pytest.mark.parametrize("source,op", [
        ("1 + 2", BinaryOp.ADD),
        ("1 - 2", BinaryOp.SUB),
        ("1 * 2", BinaryOp.MUL),
        ("1 / 2", BinaryOp.DIV),
        ("1 % 2", BinaryOp.MOD),
    ])
    def test_binary_arithmetic(self, source: str, op: BinaryOp) -> None:
        """Arithmetic operators should produce correct BinaryExpr."""
        expr = parse_expr(source)
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == op


class TestComparisonOperators:
    """Test comparison operator parsing."""
    
    @pytest.mark.parametrize("source,op", [
        ("1 == 2", BinaryOp.EQ),
        ("1 != 2", BinaryOp.NE),
        ("1 < 2", BinaryOp.LT),
        ("1 > 2", BinaryOp.GT),
        ("1 <= 2", BinaryOp.LE),
        ("1 >= 2", BinaryOp.GE),
    ])
    def test_comparison_operators(self, source: str, op: BinaryOp) -> None:
        """Comparison operators should produce correct BinaryExpr."""
        expr = parse_expr(source)
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == op


class TestLogicalOperators:
    """Test logical operator parsing."""
    
    def test_logical_and(self) -> None:
        """&& should produce BinaryExpr with AND."""
        expr = parse_expr("true && false")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOp.AND
    
    def test_logical_or(self) -> None:
        """|| should produce BinaryExpr with OR."""
        expr = parse_expr("true || false")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOp.OR
    
    def test_logical_not(self) -> None:
        """! should produce UnaryExpr with NOT."""
        expr = parse_expr("!true")
        assert isinstance(expr, UnaryExpr)
        assert expr.operator == UnaryOp.NOT


class TestUnaryOperators:
    """Test unary operator parsing."""
    
    def test_unary_negation(self) -> None:
        """-x should produce UnaryExpr with NEG."""
        expr = parse_expr("-42")
        assert isinstance(expr, UnaryExpr)
        assert expr.operator == UnaryOp.NEG
        assert isinstance(expr.operand, IntLiteral)
    
    def test_double_negation(self) -> None:
        """--x should produce nested UnaryExpr."""
        expr = parse_expr("--42")
        assert isinstance(expr, UnaryExpr)
        assert isinstance(expr.operand, UnaryExpr)
    
    def test_not_not(self) -> None:
        """!!x should produce nested UnaryExpr."""
        expr = parse_expr("!!true")
        assert isinstance(expr, UnaryExpr)
        assert isinstance(expr.operand, UnaryExpr)


class TestPrecedence:
    """Test operator precedence."""
    
    def test_mul_before_add(self) -> None:
        """1 + 2 * 3 should parse as 1 + (2 * 3)."""
        expr = parse_expr("1 + 2 * 3")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOp.ADD
        assert isinstance(expr.left, IntLiteral)
        assert isinstance(expr.right, BinaryExpr)
        assert expr.right.operator == BinaryOp.MUL
    
    def test_div_before_sub(self) -> None:
        """1 - 2 / 3 should parse as 1 - (2 / 3)."""
        expr = parse_expr("1 - 2 / 3")
        assert expr.operator == BinaryOp.SUB
        assert expr.right.operator == BinaryOp.DIV
    
    def test_comparison_before_logical(self) -> None:
        """a < b && c > d should parse as (a < b) && (c > d)."""
        expr = parse_expr("a < b && c > d")
        assert expr.operator == BinaryOp.AND
        assert expr.left.operator == BinaryOp.LT
        assert expr.right.operator == BinaryOp.GT
    
    def test_or_lowest_precedence(self) -> None:
        """a && b || c should parse as (a && b) || c."""
        expr = parse_expr("a && b || c")
        assert expr.operator == BinaryOp.OR
        assert expr.left.operator == BinaryOp.AND
    
    def test_unary_higher_than_binary(self) -> None:
        """-a + b should parse as (-a) + b."""
        expr = parse_expr("-a + b")
        assert expr.operator == BinaryOp.ADD
        assert isinstance(expr.left, UnaryExpr)
    
    def test_parentheses_override_precedence(self) -> None:
        """(1 + 2) * 3 should parse as (1 + 2) * 3."""
        expr = parse_expr("(1 + 2) * 3")
        assert expr.operator == BinaryOp.MUL
        assert expr.left.operator == BinaryOp.ADD


class TestAssociativity:
    """Test operator associativity."""
    
    def test_left_associativity_add(self) -> None:
        """1 + 2 + 3 should parse as (1 + 2) + 3."""
        expr = parse_expr("1 + 2 + 3")
        assert expr.operator == BinaryOp.ADD
        assert isinstance(expr.right, IntLiteral)
        assert expr.left.operator == BinaryOp.ADD
    
    def test_left_associativity_sub(self) -> None:
        """1 - 2 - 3 should parse as (1 - 2) - 3."""
        expr = parse_expr("1 - 2 - 3")
        assert expr.operator == BinaryOp.SUB
        assert isinstance(expr.right, IntLiteral)
        assert expr.left.operator == BinaryOp.SUB


class TestCallExpr:
    """Test function call expression parsing."""
    
    def test_call_no_args(self) -> None:
        """foo() should produce CallExpr with no arguments."""
        expr = parse_expr("foo()")
        assert isinstance(expr, CallExpr)
        assert expr.callee == "foo"
        assert expr.arguments == []
    
    def test_call_one_arg(self) -> None:
        """foo(1) should produce CallExpr with one argument."""
        expr = parse_expr("foo(1)")
        assert len(expr.arguments) == 1
        assert isinstance(expr.arguments[0], IntLiteral)
    
    def test_call_multiple_args(self) -> None:
        """foo(1, 2, 3) should produce CallExpr with three arguments."""
        expr = parse_expr("foo(1, 2, 3)")
        assert len(expr.arguments) == 3
    
    def test_call_with_expressions(self) -> None:
        """foo(a + b, c * d) should allow expression arguments."""
        expr = parse_expr("foo(a + b, c * d)")
        assert len(expr.arguments) == 2
        assert isinstance(expr.arguments[0], BinaryExpr)
        assert isinstance(expr.arguments[1], BinaryExpr)


class TestComplexExpressions:
    """Test complex nested expressions."""
    
    def test_nested_calls(self) -> None:
        """foo(bar(1)) should parse nested calls."""
        expr = parse_expr("foo(bar(1))")
        assert isinstance(expr, CallExpr)
        assert isinstance(expr.arguments[0], CallExpr)
    
    def test_complex_boolean(self) -> None:
        """Complex boolean expressions should parse correctly."""
        expr = parse_expr("(a > 0 && b < 10) || c == 5")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOp.OR
    
    def test_arithmetic_in_comparison(self) -> None:
        """a + b > c * d should parse correctly."""
        expr = parse_expr("a + b > c * d")
        assert expr.operator == BinaryOp.GT
        assert expr.left.operator == BinaryOp.ADD
        assert expr.right.operator == BinaryOp.MUL

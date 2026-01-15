"""
Parser tests — Statement parsing.

Tests that statements produce correct AST nodes.
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.ast import (
    Program,
    FnDecl,
    VarDecl,
    Block,
    IfStmt,
    WhileStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    AssignStmt,
    ExpressionStmt,
    BinaryExpr,
    CallExpr,
    Identifier,
    IntLiteral,
    BoolLiteral,
)


def parse_fn_body(body_source: str) -> Block:
    """Helper to parse function body statements."""
    source = f"fn test() -> int {{ {body_source} }}"
    lexer = Lexer(source, "test.qsr")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    prog = parser.parse()
    fn = prog.declarations[0]
    assert isinstance(fn, FnDecl)
    return fn.body


class TestBlock:
    """Test block parsing."""
    
    def test_empty_block(self) -> None:
        """Empty block should have no statements."""
        block = parse_fn_body("")
        assert block.declarations == []
    
    def test_block_with_multiple_statements(self) -> None:
        """Block should contain all statements in order."""
        block = parse_fn_body("let x: int = 1\nlet y: int = 2")
        assert len(block.declarations) == 2


class TestIfStmt:
    """Test if statement parsing."""
    
    def test_if_without_else(self) -> None:
        """if (cond) { } should produce IfStmt with no else_branch."""
        block = parse_fn_body("if (true) { let x: int = 1 }")
        stmt = block.declarations[0]
        assert isinstance(stmt, IfStmt)
        assert isinstance(stmt.condition, BoolLiteral)
        assert isinstance(stmt.then_block, Block)
        assert stmt.else_block is None
    
    def test_if_with_else(self) -> None:
        """if (cond) { } else { } should have else_branch."""
        block = parse_fn_body("if (true) { } else { let y: int = 2 }")
        stmt = block.declarations[0]
        assert isinstance(stmt, IfStmt)
        assert isinstance(stmt.else_block, Block)
    
    def test_nested_if(self) -> None:
        """Nested if should produce nested IfStmt structure."""
        block = parse_fn_body("if (true) { if (false) { } }")
        outer = block.declarations[0]
        assert isinstance(outer, IfStmt)
        inner = outer.then_block.declarations[0]
        assert isinstance(inner, IfStmt)
    
    def test_if_else_if_chain(self) -> None:
        """if-else-if chain should nest correctly."""
        block = parse_fn_body("if (true) { } else { if (false) { } }")
        stmt = block.declarations[0]
        assert isinstance(stmt, IfStmt)
        # else_branch is a Block containing another IfStmt
        assert isinstance(stmt.else_block, Block)
        nested = stmt.else_block.declarations[0]
        assert isinstance(nested, IfStmt)


class TestWhileStmt:
    """Test while statement parsing."""
    
    def test_while_basic(self) -> None:
        """while (cond) { } should produce WhileStmt."""
        block = parse_fn_body("while (true) { }")
        stmt = block.declarations[0]
        assert isinstance(stmt, WhileStmt)
        assert isinstance(stmt.condition, BoolLiteral)
        assert isinstance(stmt.body, Block)
    
    def test_while_with_body(self) -> None:
        """while body should contain statements."""
        block = parse_fn_body("while (true) { let x: int = 1 }")
        stmt = block.declarations[0]
        assert len(stmt.body.declarations) == 1
    
    def test_nested_while(self) -> None:
        """Nested while loops should produce nested WhileStmt."""
        block = parse_fn_body("while (true) { while (false) { } }")
        outer = block.declarations[0]
        inner = outer.body.declarations[0]
        assert isinstance(inner, WhileStmt)


class TestReturnStmt:
    """Test return statement parsing."""
    
    def test_return_with_value(self) -> None:
        """return expr should have expression as value."""
        block = parse_fn_body("return 42")
        stmt = block.declarations[0]
        assert isinstance(stmt, ReturnStmt)
        assert isinstance(stmt.value, IntLiteral)
        assert stmt.value.value == 42
    
    def test_return_with_complex_expression(self) -> None:
        """return should accept complex expressions."""
        block = parse_fn_body("return 1 + 2")
        stmt = block.declarations[0]
        assert isinstance(stmt.value, BinaryExpr)


class TestBreakContinue:
    """Test break and continue statement parsing."""
    
    def test_break_statement(self) -> None:
        """break should produce BreakStmt."""
        block = parse_fn_body("while (true) { break }")
        while_stmt = block.declarations[0]
        assert isinstance(while_stmt.body.declarations[0], BreakStmt)
    
    def test_continue_statement(self) -> None:
        """continue should produce ContinueStmt."""
        block = parse_fn_body("while (true) { continue }")
        while_stmt = block.declarations[0]
        assert isinstance(while_stmt.body.declarations[0], ContinueStmt)


class TestAssignStmt:
    """Test assignment statement parsing."""
    
    def test_simple_assignment(self) -> None:
        """x = 1 should produce AssignStmt."""
        block = parse_fn_body("x = 1")
        stmt = block.declarations[0]
        assert isinstance(stmt, AssignStmt)
        assert stmt.target == "x"
        assert isinstance(stmt.value, IntLiteral)
    
    def test_assignment_with_expression(self) -> None:
        """x = a + b should assign expression."""
        block = parse_fn_body("x = a + b")
        stmt = block.declarations[0]
        assert isinstance(stmt, AssignStmt)
        assert isinstance(stmt.value, BinaryExpr)


class TestExpressionStmt:
    """Test expression statement parsing."""
    
    def test_function_call_statement(self) -> None:
        """foo() as statement should produce ExpressionStmt."""
        block = parse_fn_body("foo()")
        stmt = block.declarations[0]
        assert isinstance(stmt, ExpressionStmt)
        assert isinstance(stmt.expression, CallExpr)
    
    def test_function_call_with_args(self) -> None:
        """Function call with args should parse correctly."""
        block = parse_fn_body("foo(1, 2, 3)")
        stmt = block.declarations[0]
        call = stmt.expression
        assert isinstance(call, CallExpr)
        assert len(call.arguments) == 3


class TestLocalVarDecl:
    """Test local variable declarations inside functions."""
    
    def test_local_var_decl(self) -> None:
        """Local variables should be parsed as VarDecl statements."""
        block = parse_fn_body("let x: int = 1")
        stmt = block.declarations[0]
        assert isinstance(stmt, VarDecl)
        assert stmt.name == "x"

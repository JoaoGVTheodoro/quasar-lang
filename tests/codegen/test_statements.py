"""
Tests for code generation of statements.

Covers: IfStmt, WhileStmt, ReturnStmt, BreakStmt, ContinueStmt, AssignStmt, Block

Note: Quasar grammar does NOT use semicolons as statement terminators.
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.codegen import CodeGenerator


def generate(source: str) -> str:
    """Helper to parse and generate code from Quasar source."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    return CodeGenerator().generate(ast)


class TestIfStmt:
    """Tests for if statement generation."""
    
    def test_if_simple(self):
        source = """
        fn check(x: bool) -> int {
            if x {
                return 1
            }
            return 0
        }
        """
        result = generate(source)
        expected = "def check(x):\n    if x:\n        return 1\n    return 0"
        assert result == expected
    
    def test_if_else(self):
        source = """
        fn decide(cond: bool) -> int {
            if cond {
                return 1
            } else {
                return 0
            }
        }
        """
        result = generate(source)
        expected = "def decide(cond):\n    if cond:\n        return 1\n    else:\n        return 0"
        assert result == expected
    
    def test_if_with_comparison(self):
        source = """
        fn isPositive(n: int) -> bool {
            if n > 0 {
                return true
            }
            return false
        }
        """
        result = generate(source)
        expected = "def isPositive(n):\n    if (n > 0):\n        return True\n    return False"
        assert result == expected


class TestWhileStmt:
    """Tests for while statement generation."""
    
    def test_while_simple(self):
        source = """
        fn loop(flag: bool) -> int {
            while flag {
                return 1
            }
            return 0
        }
        """
        result = generate(source)
        expected = "def loop(flag):\n    while flag:\n        return 1\n    return 0"
        assert result == expected
    
    def test_while_with_break(self):
        source = """
        fn loopBreak(x: bool) -> int {
            while true {
                break
            }
            return 0
        }
        """
        result = generate(source)
        expected = "def loopBreak(x):\n    while True:\n        break\n    return 0"
        assert result == expected
    
    def test_while_with_continue(self):
        source = """
        fn loopContinue(x: bool) -> int {
            while true {
                continue
            }
            return 0
        }
        """
        result = generate(source)
        expected = "def loopContinue(x):\n    while True:\n        continue\n    return 0"
        assert result == expected


class TestReturnStmt:
    """Tests for return statement generation."""
    
    def test_return_literal(self):
        source = "fn get() -> int { return 42 }"
        result = generate(source)
        expected = "def get():\n    return 42"
        assert result == expected
    
    def test_return_expression(self):
        source = "fn calc(x: int) -> int { return x + 1 }"
        result = generate(source)
        expected = "def calc(x):\n    return (x + 1)"
        assert result == expected


class TestAssignStmt:
    """Tests for assignment statement generation."""
    
    def test_assign_simple(self):
        source = """
        fn update() -> int {
            let x: int = 1
            x = 2
            return x
        }
        """
        result = generate(source)
        expected = "def update():\n    x = 1\n    x = 2\n    return x"
        assert result == expected
    
    def test_assign_expression(self):
        source = """
        fn increment() -> int {
            let x: int = 1
            x = x + 1
            return x
        }
        """
        result = generate(source)
        expected = "def increment():\n    x = 1\n    x = (x + 1)\n    return x"
        assert result == expected


class TestBlock:
    """Tests for block/nested scope generation."""
    
    def test_nested_if(self):
        source = """
        fn nested(a: bool, b: bool) -> int {
            if a {
                if b {
                    return 1
                }
            }
            return 0
        }
        """
        result = generate(source)
        expected = "def nested(a, b):\n    if a:\n        if b:\n            return 1\n    return 0"
        assert result == expected
    
    def test_while_in_if(self):
        source = """
        fn combo(cond: bool) -> int {
            if cond {
                while true {
                    break
                }
            }
            return 0
        }
        """
        result = generate(source)
        expected = "def combo(cond):\n    if cond:\n        while True:\n            break\n    return 0"
        assert result == expected

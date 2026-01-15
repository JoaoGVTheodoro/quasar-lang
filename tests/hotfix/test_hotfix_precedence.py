"""
Hotfix Tests — Operator Precedence

Critical regression tests for the parentheses preservation bug.
These tests would fail if binary expressions don't preserve grouping.

Bug: (a + b) * c was generating "a + b * c" instead of "(a + b) * c"
Fix: Defensive parentheses in _generate_binary_expr
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


def execute(source: str) -> str:
    """Compile and execute Quasar code."""
    python_code = compile_quasar(source)
    result = subprocess.run(
        ["python", "-c", python_code],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return result.stdout.strip()


# =============================================================================
# Math Precedence Tests
# =============================================================================

class TestMathPrecedence:
    """Test arithmetic operator precedence preservation."""
    
    def test_add_then_multiply(self):
        """(2 + 3) * 4 = 20, not 14."""
        source = '''
        let x: int = (2 + 3) * 4
        print("{}", x)
        '''
        assert execute(source) == "20"
    
    def test_subtract_then_multiply(self):
        """(10 - 3) * 2 = 14, not 4."""
        source = '''
        let x: int = (10 - 3) * 2
        print("{}", x)
        '''
        assert execute(source) == "14"
    
    def test_add_then_divide(self):
        """(6 + 4) / 2 = 5, not 8."""
        source = '''
        let x: int = (6 + 4) / 2
        print("{}", x)
        '''
        # Python division returns float
        output = execute(source)
        assert output in ["5", "5.0"]
    
    def test_nested_parentheses(self):
        """((2 + 3) * 4) + 1 = 21."""
        source = '''
        let x: int = ((2 + 3) * 4) + 1
        print("{}", x)
        '''
        assert execute(source) == "21"
    
    def test_complex_grouping(self):
        """(1 + 2) * (3 + 4) = 21, not 1 + 6 + 4 = 11."""
        source = '''
        let x: int = (1 + 2) * (3 + 4)
        print("{}", x)
        '''
        assert execute(source) == "21"
    
    def test_division_before_add(self):
        """10 / (2 + 3) = 2, not 7."""
        source = '''
        let x: float = 10.0 / (2.0 + 3.0)
        print("{}", x)
        '''
        assert execute(source) == "2.0"


# =============================================================================
# Logic Precedence Tests
# =============================================================================

class TestLogicPrecedence:
    """Test logical operator precedence preservation."""
    
    def test_or_then_and(self):
        """(true || false) && false = False.
        Without parens: true || (false && false) = true || false = True.
        """
        source = '''
        let res: bool = (true || false) && false
        print("{}", res)
        '''
        assert execute(source) == "False"
    
    def test_and_then_or(self):
        """(false && true) || true = True."""
        source = '''
        let res: bool = (false && true) || true
        print("{}", res)
        '''
        assert execute(source) == "True"
    
    def test_complex_logic(self):
        """((true && false) || true) && true = True."""
        source = '''
        let res: bool = ((true && false) || true) && true
        print("{}", res)
        '''
        assert execute(source) == "True"


# =============================================================================
# Comparison Precedence Tests
# =============================================================================

class TestComparisonPrecedence:
    """Test comparison with arithmetic precedence."""
    
    def test_grouped_comparison(self):
        """(2 + 3) > 4 = True."""
        source = '''
        let res: bool = (2 + 3) > 4
        print("{}", res)
        '''
        assert execute(source) == "True"
    
    def test_both_sides_grouped(self):
        """(2 + 2) == (1 + 3) = True."""
        source = '''
        let res: bool = (2 + 2) == (1 + 3)
        print("{}", res)
        '''
        assert execute(source) == "True"


# =============================================================================
# Integration: Average Calculation (Original Bug)
# =============================================================================

class TestAverageCalculation:
    """The original bug case: average with division."""
    
    def test_average_with_parens(self):
        """(10 + 20 + 30) / 3 = 20, not 10 + 20 + 10 = 40."""
        source = '''
        let a: float = 10.0
        let b: float = 20.0
        let c: float = 30.0
        let avg: float = (a + b + c) / 3.0
        print("{}", avg)
        '''
        assert execute(source) == "20.0"
    
    def test_sum_then_divide(self):
        """Validate the hotfix works for the original issue."""
        source = '''
        let x: int = (1 + 2 + 3 + 4) * 10
        print("{}", x)
        '''
        # 1+2+3+4 = 10, * 10 = 100
        assert execute(source) == "100"

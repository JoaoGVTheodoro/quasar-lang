"""
Phase 6.3 Tests — For Loops and Range Expressions

Tests for the for loop statement and range expressions:
- Range expressions (0..10)
- List iteration (for item in list)
- Loop variable scoping and shadowing
- Type inference in loops
- Nested loops
- Error handling (E0504, E0505)
"""

import pytest
from quasar.lexer import Lexer
from quasar.lexer.token_type import TokenType
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.semantic.errors import SemanticError
from quasar.codegen import CodeGenerator
from quasar.ast import (
    Program,
    ForStmt,
    RangeExpr,
    IntLiteral,
    Identifier,
    ListLiteral,
)


# =============================================================================
# Helper Functions
# =============================================================================


def lex(source: str) -> list:
    """Tokenize source code."""
    return Lexer(source, "<test>").tokenize()


def parse(source: str) -> Program:
    """Parse source to AST."""
    tokens = lex(source)
    return Parser(tokens).parse()


def analyze(source: str) -> Program:
    """Parse and analyze source."""
    ast = parse(source)
    return SemanticAnalyzer().analyze(ast)


def compile_to_python(source: str) -> str:
    """Compile source to Python code."""
    ast = analyze(source)
    return CodeGenerator().generate(ast)


def run_quasar(source: str) -> str:
    """Compile and run Quasar code, return stdout."""
    import io
    import sys
    
    python_code = compile_to_python(source)
    
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        exec(python_code, {})
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout
    
    return output


# =============================================================================
# Lexer Tests — FOR, IN, DOTDOT tokens
# =============================================================================


class TestLexerTokens:
    """Test new tokens for Phase 6.3."""
    
    def test_for_keyword(self) -> None:
        """FOR is recognized as keyword."""
        tokens = lex("for")
        assert tokens[0].type == TokenType.FOR
    
    def test_in_keyword(self) -> None:
        """IN is recognized as keyword."""
        tokens = lex("in")
        assert tokens[0].type == TokenType.IN
    
    def test_dotdot_operator(self) -> None:
        """DOTDOT (..) is recognized as operator."""
        tokens = lex("..")
        assert tokens[0].type == TokenType.DOTDOT
    
    def test_range_expression_tokens(self) -> None:
        """0..10 produces correct token sequence."""
        tokens = lex("0..10")
        assert tokens[0].type == TokenType.INT_LITERAL
        assert tokens[0].literal == 0
        assert tokens[1].type == TokenType.DOTDOT
        assert tokens[2].type == TokenType.INT_LITERAL
        assert tokens[2].literal == 10
    
    def test_for_loop_tokens(self) -> None:
        """for i in 0..10 produces correct token sequence."""
        tokens = lex("for i in 0..10")
        assert tokens[0].type == TokenType.FOR
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].lexeme == "i"
        assert tokens[2].type == TokenType.IN
        assert tokens[3].type == TokenType.INT_LITERAL
        assert tokens[4].type == TokenType.DOTDOT
        assert tokens[5].type == TokenType.INT_LITERAL


# =============================================================================
# Parser Tests — ForStmt and RangeExpr
# =============================================================================


class TestParserForStmt:
    """Test parsing of for statements."""
    
    def test_for_range_basic(self) -> None:
        """Parse for i in 0..10 { }."""
        ast = parse("for i in 0..10 { }")
        assert len(ast.declarations) == 1
        stmt = ast.declarations[0]
        assert isinstance(stmt, ForStmt)
        assert stmt.variable == "i"
        assert isinstance(stmt.iterable, RangeExpr)
    
    def test_for_range_with_body(self) -> None:
        """Parse for loop with body."""
        ast = parse("for x in 1..5 { print(x) }")
        stmt = ast.declarations[0]
        assert isinstance(stmt, ForStmt)
        assert stmt.variable == "x"
        assert len(stmt.body.declarations) == 1
    
    def test_for_list_iteration(self) -> None:
        """Parse for item in list { }."""
        ast = parse("for item in [1, 2, 3] { }")
        stmt = ast.declarations[0]
        assert isinstance(stmt, ForStmt)
        assert stmt.variable == "item"
        assert isinstance(stmt.iterable, ListLiteral)
    
    def test_for_identifier_iterable(self) -> None:
        """Parse for item in variable { }."""
        ast = parse("""
        let nums: [int] = [1, 2]
        for n in nums { }
        """)
        stmt = ast.declarations[1]
        assert isinstance(stmt, ForStmt)
        assert isinstance(stmt.iterable, Identifier)
    
    def test_range_expr_structure(self) -> None:
        """RangeExpr has correct start and end."""
        ast = parse("for i in 5..10 { }")
        stmt = ast.declarations[0]
        range_expr = stmt.iterable
        assert isinstance(range_expr, RangeExpr)
        assert isinstance(range_expr.start, IntLiteral)
        assert range_expr.start.value == 5
        assert isinstance(range_expr.end, IntLiteral)
        assert range_expr.end.value == 10


# =============================================================================
# Semantic Analysis Tests — Valid Cases
# =============================================================================


class TestSemanticForLoopValid:
    """Test semantic analysis of valid for loops."""
    
    def test_for_range_valid(self) -> None:
        """For loop with range passes analysis."""
        analyze("for i in 0..10 { }")
    
    def test_for_list_valid(self) -> None:
        """For loop with list passes analysis."""
        analyze("for x in [1, 2, 3] { }")
    
    def test_for_variable_use_in_body(self) -> None:
        """Loop variable is accessible in body."""
        analyze("for i in 0..5 { print(i) }")
    
    def test_for_list_element_type(self) -> None:
        """Loop variable has correct element type from list."""
        analyze("""
        for s in ["a", "b", "c"] {
            let x: str = s
        }
        """)
    
    def test_for_range_int_variable(self) -> None:
        """Loop variable is int for range iteration."""
        analyze("""
        for i in 0..10 {
            let x: int = i + 1
        }
        """)
    
    def test_for_nested_loops(self) -> None:
        """Nested for loops work correctly."""
        analyze("""
        for i in 0..3 {
            for j in 0..3 {
                print(i + j)
            }
        }
        """)
    
    def test_for_variable_shadowing(self) -> None:
        """Loop variable shadows outer variable."""
        analyze("""
        let i: int = 100
        for i in 0..5 {
            print(i)
        }
        print(i)
        """)
    
    def test_for_with_break(self) -> None:
        """Break is valid inside for loop."""
        analyze("""
        for i in 0..10 {
            if i == 5 {
                break
            }
        }
        """)
    
    def test_for_with_continue(self) -> None:
        """Continue is valid inside for loop."""
        analyze("""
        for i in 0..10 {
            if i % 2 == 0 {
                continue
            }
            print(i)
        }
        """)


# =============================================================================
# Semantic Analysis Tests — Error Cases
# =============================================================================


class TestSemanticForLoopErrors:
    """Test semantic errors for for loops."""
    
    def test_e0504_range_start_not_int(self) -> None:
        """E0504: Range start must be int."""
        with pytest.raises(SemanticError) as exc:
            analyze('for i in "a"..10 { }')
        assert exc.value.code == "E0504"
        assert "range start must be int" in exc.value.message
    
    def test_e0504_range_end_not_int(self) -> None:
        """E0504: Range end must be int."""
        with pytest.raises(SemanticError) as exc:
            analyze('for i in 0.."z" { }')
        assert exc.value.code == "E0504"
        assert "range end must be int" in exc.value.message
    
    def test_e0504_range_float_start(self) -> None:
        """E0504: Range with float start."""
        with pytest.raises(SemanticError) as exc:
            analyze("for i in 1.5..10 { }")
        assert exc.value.code == "E0504"
    
    def test_e0504_range_bool_operands(self) -> None:
        """E0504: Range with bool operands."""
        with pytest.raises(SemanticError) as exc:
            analyze("for i in true..false { }")
        assert exc.value.code == "E0504"
    
    def test_e0505_iterate_over_int(self) -> None:
        """E0505: Cannot iterate over int."""
        with pytest.raises(SemanticError) as exc:
            analyze("for i in 42 { }")
        assert exc.value.code == "E0505"
        assert "cannot iterate over" in exc.value.message
    
    def test_e0505_iterate_over_string(self) -> None:
        """E0505: Cannot iterate over string."""
        with pytest.raises(SemanticError) as exc:
            analyze('for c in "hello" { }')
        assert exc.value.code == "E0505"
    
    def test_e0505_iterate_over_bool(self) -> None:
        """E0505: Cannot iterate over bool."""
        with pytest.raises(SemanticError) as exc:
            analyze("for b in true { }")
        assert exc.value.code == "E0505"


# =============================================================================
# Code Generation Tests
# =============================================================================


class TestCodeGenForLoop:
    """Test Python code generation for for loops."""
    
    def test_codegen_for_range(self) -> None:
        """For range generates Python range()."""
        code = compile_to_python("for i in 0..5 { }")
        assert "for i in range(0, 5):" in code
    
    def test_codegen_for_list(self) -> None:
        """For list generates Python for-in."""
        code = compile_to_python("for x in [1, 2, 3] { }")
        assert "for x in [1, 2, 3]:" in code
    
    def test_codegen_for_with_body(self) -> None:
        """For loop body is indented correctly."""
        code = compile_to_python("for i in 0..3 { print(i) }")
        lines = code.split("\n")
        # Find print line
        print_line = [l for l in lines if "print(i)" in l][0]
        assert print_line.startswith("    ")  # Indented


# =============================================================================
# End-to-End Tests
# =============================================================================


class TestE2EForLoop:
    """End-to-end tests for for loops."""
    
    def test_e2e_range_sum(self) -> None:
        """Sum integers in a range."""
        output = run_quasar("""
        let sum: int = 0
        for i in 0..5 {
            sum = sum + i
        }
        print(sum)
        """)
        assert output.strip() == "10"  # 0+1+2+3+4 = 10
    
    def test_e2e_list_iteration(self) -> None:
        """Iterate over list elements."""
        output = run_quasar("""
        for x in [10, 20, 30] {
            print(x)
        }
        """)
        assert output.strip() == "10\n20\n30"
    
    def test_e2e_nested_loops(self) -> None:
        """Nested loops produce correct output."""
        output = run_quasar("""
        for i in 0..2 {
            for j in 0..2 {
                print(i * 10 + j)
            }
        }
        """)
        # 0*10+0=0, 0*10+1=1, 1*10+0=10, 1*10+1=11
        assert output.strip() == "0\n1\n10\n11"
    
    def test_e2e_break_in_for(self) -> None:
        """Break exits for loop early."""
        output = run_quasar("""
        for i in 0..10 {
            if i == 3 {
                break
            }
            print(i)
        }
        """)
        assert output.strip() == "0\n1\n2"
    
    def test_e2e_continue_in_for(self) -> None:
        """Continue skips to next iteration."""
        output = run_quasar("""
        for i in 0..5 {
            if i == 2 {
                continue
            }
            print(i)
        }
        """)
        assert output.strip() == "0\n1\n3\n4"
    
    def test_e2e_shadowing(self) -> None:
        """Loop variable shadows outer variable during loop.
        
        Note: Since we transpile to Python, Python's scoping rules apply.
        In Python, for-loop variables persist after the loop and overwrite
        the outer variable if they share the same name. This means the
        outer 'i' becomes 2 (last value) after the loop.
        """
        output = run_quasar("""
        let i: int = 99
        for i in 0..3 {
            print(i)
        }
        print(i)
        """)
        # Python behavior: i is 2 after the loop (last iteration value)
        assert output.strip() == "0\n1\n2\n2"
    
    def test_e2e_string_list_iteration(self) -> None:
        """Iterate over string list."""
        output = run_quasar("""
        for name in ["Alice", "Bob"] {
            print(name)
        }
        """)
        assert output.strip() == "Alice\nBob"
    
    def test_e2e_for_with_list_variable(self) -> None:
        """Iterate over list stored in variable."""
        output = run_quasar("""
        let nums: [int] = [5, 10, 15]
        let total: int = 0
        for n in nums {
            total = total + n
        }
        print(total)
        """)
        assert output.strip() == "30"
    
    def test_e2e_for_modify_list_element(self) -> None:
        """Use loop to modify list elements via index."""
        output = run_quasar("""
        let nums: [int] = [1, 2, 3]
        for i in 0..3 {
            nums[i] = nums[i] * 2
        }
        print(nums[0])
        print(nums[1])
        print(nums[2])
        """)
        assert output.strip() == "2\n4\n6"
    
    def test_e2e_for_with_len(self) -> None:
        """Use len() to determine loop range."""
        output = run_quasar("""
        let items: [int] = [10, 20, 30, 40]
        for i in 0..len(items) {
            print(items[i])
        }
        """)
        assert output.strip() == "10\n20\n30\n40"

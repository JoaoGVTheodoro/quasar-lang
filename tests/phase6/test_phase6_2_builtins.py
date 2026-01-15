"""
Phase 6.2 Tests: Built-in Functions (len, push)

Tests for:
- len(list): Returns length of list
- push(list, value): Appends value to list
- Semantic errors E0506, E0507
- Integration tests with execution
"""

import pytest
import subprocess
import tempfile
from pathlib import Path

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.semantic.errors import SemanticError
from quasar.codegen import CodeGenerator


# =============================================================================
# Helper Functions
# =============================================================================

def parse(source: str):
    """Parse source and return AST."""
    lexer = Lexer(source, filename="<stdin>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def analyze(source: str):
    """Parse and analyze source."""
    ast = parse(source)
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast)


def generate(source: str) -> str:
    """Parse, analyze, and generate Python code."""
    ast = parse(source)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    generator = CodeGenerator()
    return generator.generate(ast)


def execute(source: str) -> str:
    """Compile and execute Quasar code, return stdout."""
    code = generate(source)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        result = subprocess.run(
            ['python', f.name],
            capture_output=True,
            text=True
        )
        Path(f.name).unlink()
    return result.stdout


# =============================================================================
# len() Valid Cases
# =============================================================================

class TestLenValid:
    """Test valid uses of len() built-in."""
    
    def test_len_literal_list(self):
        """len([1, 2, 3]) is valid."""
        analyze("let x: int = len([1, 2, 3])")
    
    def test_len_variable(self):
        """len(variable) is valid."""
        analyze("let nums: [int] = [1, 2, 3]\nlet n: int = len(nums)")
    
    def test_len_empty_list(self):
        """len([]) is valid (returns 0)."""
        analyze("let x: [int] = []\nlet n: int = len(x)")
    
    def test_len_string_list(self):
        """len() works on [str]."""
        analyze('let names: [str] = ["a", "b"]\nlet n: int = len(names)')
    
    def test_len_nested_list(self):
        """len() works on [[int]]."""
        analyze("let m: [[int]] = [[1, 2], [3, 4]]\nlet n: int = len(m)")


# =============================================================================
# len() Invalid Cases (E0507)
# =============================================================================

class TestLenInvalid:
    """Test E0507 errors for len()."""
    
    def test_len_no_args(self):
        """E0507: len() with no arguments."""
        with pytest.raises(SemanticError) as exc:
            analyze("let x: int = len()")
        assert exc.value.code == "E0507"
        assert "1 argument" in exc.value.message
    
    def test_len_too_many_args(self):
        """E0507: len() with too many arguments."""
        with pytest.raises(SemanticError) as exc:
            analyze("let x: int = len([1], [2])")
        assert exc.value.code == "E0507"
        assert "1 argument" in exc.value.message
    
    def test_len_int_arg(self):
        """E0507: len(int) is error."""
        with pytest.raises(SemanticError) as exc:
            analyze("let x: int = len(42)")
        assert exc.value.code == "E0507"
        assert "list" in exc.value.message
    
    def test_len_str_arg(self):
        """E0507: len(str) is error (strings not indexable in Quasar)."""
        with pytest.raises(SemanticError) as exc:
            analyze('let x: int = len("hello")')
        assert exc.value.code == "E0507"
    
    def test_len_bool_arg(self):
        """E0507: len(bool) is error."""
        with pytest.raises(SemanticError) as exc:
            analyze("let x: int = len(true)")
        assert exc.value.code == "E0507"


# =============================================================================
# push() Valid Cases
# =============================================================================

class TestPushValid:
    """Test valid uses of push() built-in."""
    
    def test_push_int(self):
        """push(list, int) is valid."""
        analyze("let nums: [int] = [1, 2]\npush(nums, 3)")
    
    def test_push_str(self):
        """push(list, str) is valid."""
        analyze('let names: [str] = ["a"]\npush(names, "b")')
    
    def test_push_to_empty_list(self):
        """push() to empty list is valid."""
        analyze("let nums: [int] = []\npush(nums, 1)")
    
    def test_push_nested_list(self):
        """push() nested list element."""
        analyze("let m: [[int]] = [[1, 2]]\npush(m, [3, 4])")


# =============================================================================
# push() Invalid Cases (E0506)
# =============================================================================

class TestPushInvalid:
    """Test E0506 errors for push()."""
    
    def test_push_no_args(self):
        """E0506: push() with no arguments."""
        with pytest.raises(SemanticError) as exc:
            analyze("push()")
        assert exc.value.code == "E0506"
        assert "2 arguments" in exc.value.message
    
    def test_push_one_arg(self):
        """E0506: push() with one argument."""
        with pytest.raises(SemanticError) as exc:
            analyze("let x: [int] = [1]\npush(x)")
        assert exc.value.code == "E0506"
        assert "2 arguments" in exc.value.message
    
    def test_push_non_list(self):
        """E0506: push(int, val) is error."""
        with pytest.raises(SemanticError) as exc:
            analyze("let x: int = 1\npush(x, 2)")
        assert exc.value.code == "E0506"
        assert "list" in exc.value.message
    
    def test_push_type_mismatch(self):
        """E0506: push(int_list, str) is error."""
        with pytest.raises(SemanticError) as exc:
            analyze('let nums: [int] = [1, 2]\npush(nums, "hello")')
        assert exc.value.code == "E0506"
        assert "str" in exc.value.message
        assert "int" in exc.value.message
    
    def test_push_nested_type_mismatch(self):
        """E0506: push([[int]], int) is error (needs [int])."""
        with pytest.raises(SemanticError) as exc:
            analyze("let m: [[int]] = [[1]]\npush(m, 2)")
        assert exc.value.code == "E0506"


# =============================================================================
# Code Generation Tests
# =============================================================================

class TestCodeGen:
    """Test code generation for built-ins."""
    
    def test_codegen_len(self):
        """len() generates Python len()."""
        code = generate("let nums: [int] = [1, 2, 3]\nlet n: int = len(nums)")
        assert "len(nums)" in code
    
    def test_codegen_push(self):
        """push() generates Python .append()."""
        code = generate("let nums: [int] = [1, 2]\npush(nums, 3)")
        assert "nums.append(3)" in code
    
    def test_codegen_push_expression(self):
        """push() with expression value."""
        code = generate("let nums: [int] = [1]\npush(nums, 1 + 2)")
        assert "nums.append((1 + 2))" in code


# =============================================================================
# Integration Tests (E2E)
# =============================================================================

class TestIntegration:
    """End-to-end tests with execution."""
    
    def test_e2e_len_literal(self):
        """len([1, 2, 3]) == 3"""
        output = execute("print(len([1, 2, 3]))")
        assert output.strip() == "3"
    
    def test_e2e_len_empty(self):
        """len([]) == 0"""
        output = execute("let x: [int] = []\nprint(len(x))")
        assert output.strip() == "0"
    
    def test_e2e_push_and_len(self):
        """Push then check len."""
        source = """
let nums: [int] = []
push(nums, 10)
push(nums, 20)
print(len(nums))
"""
        output = execute(source)
        assert output.strip() == "2"
    
    def test_e2e_push_and_access(self):
        """Push then access element."""
        source = """
let nums: [int] = [1, 2]
push(nums, 3)
print(nums[2])
"""
        output = execute(source)
        assert output.strip() == "3"
    
    def test_e2e_complex_workflow(self):
        """Build list dynamically and print."""
        source = """
let nums: [int] = []
push(nums, 10)
push(nums, 20)
push(nums, 30)
print(nums[0], nums[1], nums[2], sep=", ")
print(len(nums))
"""
        output = execute(source)
        lines = output.strip().split('\n')
        assert lines[0] == "10, 20, 30"
        assert lines[1] == "3"
    
    def test_e2e_nested_push(self):
        """Push to nested list."""
        source = """
let m: [[int]] = []
push(m, [1, 2])
push(m, [3, 4])
print(len(m))
print(m[0][0], m[1][1])
"""
        output = execute(source)
        lines = output.strip().split('\n')
        assert lines[0] == "2"
        assert lines[1] == "1 4"
    
    def test_e2e_len_in_condition(self):
        """Use len() in condition."""
        source = """
let nums: [int] = [1, 2, 3]
if len(nums) > 2 {
    print("big")
} else {
    print("small")
}
"""
        output = execute(source)
        assert output.strip() == "big"
    
    def test_e2e_len_in_expression(self):
        """Use len() in arithmetic expression."""
        source = """
let nums: [int] = [1, 2, 3, 4, 5]
let doubled: int = len(nums) * 2
print(doubled)
"""
        output = execute(source)
        assert output.strip() == "10"

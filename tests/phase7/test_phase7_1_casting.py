"""
Phase 7.1 Tests — Type Casting Functions

Tests for type conversion built-ins: int(), float(), str(), bool()

These functions enable processing user input (always str) into numeric types.
"""

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer, SemanticError
from quasar.codegen import CodeGenerator


def analyze(source: str):
    """Helper to run semantic analysis."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    return SemanticAnalyzer().analyze(ast)


def compile_to_python(source: str) -> str:
    """Helper to compile Quasar to Python."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    ast = SemanticAnalyzer().analyze(ast)
    return CodeGenerator().generate(ast)


def execute(source: str) -> str:
    """Compile and execute, returning stdout."""
    python_code = compile_to_python(source)
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        exec(python_code, {})
        return sys.stdout.getvalue().strip()
    finally:
        sys.stdout = old_stdout


# =============================================================================
# int() Conversion
# =============================================================================

class TestIntConversion:
    """Test int() type casting."""
    
    def test_int_from_string_literal(self):
        """int("123") converts string to int."""
        source = """
        let x: int = int("123")
        print("{}", x)
        """
        assert execute(source) == "123"
    
    def test_int_from_float_literal(self):
        """int(12.7) truncates float to int."""
        source = """
        let x: int = int(12.7)
        print("{}", x)
        """
        assert execute(source) == "12"
    
    def test_int_from_bool_true(self):
        """int(true) converts to 1."""
        source = """
        let x: int = int(true)
        print("{}", x)
        """
        assert execute(source) == "1"
    
    def test_int_from_bool_false(self):
        """int(false) converts to 0."""
        source = """
        let x: int = int(false)
        print("{}", x)
        """
        assert execute(source) == "0"
    
    def test_int_from_int_identity(self):
        """int(42) is identity for int."""
        source = """
        let x: int = int(42)
        print("{}", x)
        """
        assert execute(source) == "42"
    
    def test_int_from_variable(self):
        """int(var) works with variables."""
        source = """
        let s: str = "999"
        let x: int = int(s)
        print("{}", x)
        """
        assert execute(source) == "999"


# =============================================================================
# float() Conversion
# =============================================================================

class TestFloatConversion:
    """Test float() type casting."""
    
    def test_float_from_string(self):
        """float("3.14") converts string to float."""
        source = """
        let x: float = float("3.14")
        print("{}", x)
        """
        assert execute(source) == "3.14"
    
    def test_float_from_int(self):
        """float(42) converts int to float."""
        source = """
        let x: float = float(42)
        print("{}", x)
        """
        assert execute(source) == "42.0"
    
    def test_float_from_bool(self):
        """float(true) converts to 1.0."""
        source = """
        let x: float = float(true)
        print("{}", x)
        """
        assert execute(source) == "1.0"
    
    def test_float_identity(self):
        """float(3.14) is identity for float."""
        source = """
        let x: float = float(3.14)
        print("{}", x)
        """
        assert execute(source) == "3.14"


# =============================================================================
# str() Conversion
# =============================================================================

class TestStrConversion:
    """Test str() type casting."""
    
    def test_str_from_int(self):
        """str(123) converts int to string."""
        source = """
        let s: str = str(123)
        print("{}", s)
        """
        assert execute(source) == "123"
    
    def test_str_from_float(self):
        """str(3.14) converts float to string."""
        source = """
        let s: str = str(3.14)
        print("{}", s)
        """
        assert execute(source) == "3.14"
    
    def test_str_from_bool_true(self):
        """str(true) converts to "True"."""
        source = """
        let s: str = str(true)
        print("{}", s)
        """
        assert execute(source) == "True"
    
    def test_str_from_bool_false(self):
        """str(false) converts to "False"."""
        source = """
        let s: str = str(false)
        print("{}", s)
        """
        assert execute(source) == "False"
    
    def test_str_identity(self):
        """str("hello") is identity for string."""
        source = """
        let s: str = str("hello")
        print("{}", s)
        """
        assert execute(source) == "hello"


# =============================================================================
# bool() Conversion
# =============================================================================

class TestBoolConversion:
    """Test bool() type casting."""
    
    def test_bool_from_int_nonzero(self):
        """bool(1) is true."""
        source = """
        let b: bool = bool(1)
        print("{}", b)
        """
        assert execute(source) == "True"
    
    def test_bool_from_int_zero(self):
        """bool(0) is false."""
        source = """
        let b: bool = bool(0)
        print("{}", b)
        """
        assert execute(source) == "False"
    
    def test_bool_from_string_nonempty(self):
        """bool("x") is true for non-empty string."""
        source = """
        let b: bool = bool("hello")
        print("{}", b)
        """
        assert execute(source) == "True"
    
    def test_bool_from_string_empty(self):
        """bool("") is false for empty string."""
        source = """
        let b: bool = bool("")
        print("{}", b)
        """
        assert execute(source) == "False"
    
    def test_bool_from_float_nonzero(self):
        """bool(1.5) is true."""
        source = """
        let b: bool = bool(1.5)
        print("{}", b)
        """
        assert execute(source) == "True"
    
    def test_bool_identity(self):
        """bool(true) is identity."""
        source = """
        let b: bool = bool(true)
        print("{}", b)
        """
        assert execute(source) == "True"


# =============================================================================
# Error Cases (E0602)
# =============================================================================

class TestCastingErrors:
    """Test error cases for type casting functions."""
    
    def test_int_no_args(self):
        """E0602: int() requires exactly 1 argument."""
        source = """
        let x: int = int()
        """
        with pytest.raises(SemanticError) as exc:
            analyze(source)
        assert exc.value.code == "E0602"
        assert "exactly 1 argument" in exc.value.message
    
    def test_float_two_args(self):
        """E0602: float() with 2 args fails."""
        source = """
        let x: float = float(1, 2)
        """
        with pytest.raises(SemanticError) as exc:
            analyze(source)
        assert exc.value.code == "E0602"
    
    def test_str_no_args(self):
        """E0602: str() requires exactly 1 argument."""
        source = """
        let s: str = str()
        """
        with pytest.raises(SemanticError) as exc:
            analyze(source)
        assert exc.value.code == "E0602"
    
    def test_bool_three_args(self):
        """E0602: bool() with 3 args fails."""
        source = """
        let b: bool = bool(1, 2, 3)
        """
        with pytest.raises(SemanticError) as exc:
            analyze(source)
        assert exc.value.code == "E0602"
    
    def test_cast_type_mismatch(self):
        """E0100: Assigning int() result to wrong type."""
        source = """
        let s: str = int("42")
        """
        with pytest.raises(SemanticError) as exc:
            analyze(source)
        assert exc.value.code == "E0100"


# =============================================================================
# Code Generation
# =============================================================================

class TestCastingCodeGen:
    """Test code generation for casting functions."""
    
    def test_codegen_int(self):
        """int(x) generates Python int(x)."""
        source = """
        let x: int = int("42")
        """
        python = compile_to_python(source)
        assert 'x = int("42")' in python
    
    def test_codegen_float(self):
        """float(x) generates Python float(x)."""
        source = """
        let x: float = float(10)
        """
        python = compile_to_python(source)
        assert "x = float(10)" in python
    
    def test_codegen_str(self):
        """str(x) generates Python str(x)."""
        source = """
        let s: str = str(123)
        """
        python = compile_to_python(source)
        assert "s = str(123)" in python
    
    def test_codegen_bool(self):
        """bool(x) generates Python bool(x)."""
        source = """
        let b: bool = bool(0)
        """
        python = compile_to_python(source)
        assert "b = bool(0)" in python


# =============================================================================
# Integration: Input + Casting
# =============================================================================

class TestInputCastingIntegration:
    """Test combining input() with type casting."""
    
    def test_int_input_semantic(self):
        """int(input()) is semantically valid."""
        source = """
        let age: int = int(input("Age: "))
        """
        ast = analyze(source)
        assert ast is not None
    
    def test_float_input_semantic(self):
        """float(input()) is semantically valid."""
        source = """
        let price: float = float(input("Price: "))
        """
        ast = analyze(source)
        assert ast is not None
    
    def test_codegen_int_input(self):
        """int(input("prompt")) generates correctly."""
        source = """
        let n: int = int(input("Enter number: "))
        """
        python = compile_to_python(source)
        assert 'n = int(input("Enter number: "))' in python
    
    def test_chained_conversions(self):
        """Chained conversions work: str(int(float(...)))"""
        source = """
        let s: str = str(int(3.99))
        print("{}", s)
        """
        assert execute(source) == "3"
    
    def test_calculator_pattern(self):
        """Common calculator pattern compiles."""
        source = """
        fn add(a: int, b: int) -> int {
            return a + b
        }
        
        let x: int = int("10")
        let y: int = int("20")
        let result: int = add(x, y)
        print("{}", result)
        """
        assert execute(source) == "30"

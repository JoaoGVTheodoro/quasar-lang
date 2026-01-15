"""
Phase 6.1 Tests: Index Access & Mutation

Tests for:
- IndexExpr parsing and code generation (list[0], matrix[i][j])
- IndexAssignStmt parsing and code generation (list[0] = val)
- Semantic errors E0501, E0502, E0503
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
from quasar.ast import IndexExpr, IndexAssignStmt, IntLiteral, Identifier


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
# Parser Tests: IndexExpr
# =============================================================================

class TestParserIndexExpr:
    """Test parsing of index expressions."""
    
    def test_parse_simple_index(self):
        """let x: [int] = [1, 2, 3]
           let y: int = x[0]"""
        ast = parse("let x: [int] = [1, 2, 3]\nlet y: int = x[0]")
        decl = ast.declarations[1]
        assert isinstance(decl.initializer, IndexExpr)
        assert isinstance(decl.initializer.target, Identifier)
        assert decl.initializer.target.name == "x"
        assert isinstance(decl.initializer.index, IntLiteral)
        assert decl.initializer.index.value == 0
    
    def test_parse_index_with_expression(self):
        """let x: [int] = [1, 2, 3]
           let y: int = x[1 + 1]"""
        ast = parse("let x: [int] = [1, 2, 3]\nlet y: int = x[1 + 1]")
        decl = ast.declarations[1]
        assert isinstance(decl.initializer, IndexExpr)
    
    def test_parse_nested_index(self):
        """let m: [[int]] = [[1, 2], [3, 4]]
           let v: int = m[0][1]"""
        ast = parse("let m: [[int]] = [[1, 2], [3, 4]]\nlet v: int = m[0][1]")
        decl = ast.declarations[1]
        # m[0][1] is (m[0])[1]
        assert isinstance(decl.initializer, IndexExpr)
        assert isinstance(decl.initializer.target, IndexExpr)
        assert decl.initializer.target.target.name == "m"
    
    def test_parse_index_in_expression(self):
        """let x: [int] = [10, 20]
           let y: int = x[0] + x[1]"""
        ast = parse("let x: [int] = [10, 20]\nlet y: int = x[0] + x[1]")
        decl = ast.declarations[1]
        assert decl.initializer.operator is not None  # Binary expression


# =============================================================================
# Parser Tests: IndexAssignStmt
# =============================================================================

class TestParserIndexAssignStmt:
    """Test parsing of index assignment statements."""
    
    def test_parse_simple_index_assign(self):
        """let x: [int] = [1, 2, 3]
           x[0] = 10"""
        ast = parse("let x: [int] = [1, 2, 3]\nx[0] = 10")
        stmt = ast.declarations[1]
        assert isinstance(stmt, IndexAssignStmt)
        assert isinstance(stmt.target, IndexExpr)
        assert isinstance(stmt.value, IntLiteral)
    
    def test_parse_nested_index_assign(self):
        """let m: [[int]] = [[1, 2], [3, 4]]
           m[0][1] = 99"""
        ast = parse("let m: [[int]] = [[1, 2], [3, 4]]\nm[0][1] = 99")
        stmt = ast.declarations[1]
        assert isinstance(stmt, IndexAssignStmt)
        assert isinstance(stmt.target, IndexExpr)
        assert isinstance(stmt.target.target, IndexExpr)
    
    def test_parse_index_assign_with_expression(self):
        """let x: [int] = [1, 2, 3]
           x[0] = x[1] + x[2]"""
        ast = parse("let x: [int] = [1, 2, 3]\nx[0] = x[1] + x[2]")
        stmt = ast.declarations[1]
        assert isinstance(stmt, IndexAssignStmt)


# =============================================================================
# Semantic Tests: Valid Cases
# =============================================================================

class TestSemanticValidIndex:
    """Test semantic validation of valid index operations."""
    
    def test_valid_index_read(self):
        """Valid: read from list with int index."""
        analyze("let x: [int] = [1, 2, 3]\nlet y: int = x[0]")
    
    def test_valid_index_read_expression(self):
        """Valid: read with expression index."""
        analyze("let x: [int] = [1, 2, 3]\nlet y: int = x[1 + 1]")
    
    def test_valid_nested_index_read(self):
        """Valid: read from nested list."""
        analyze("let m: [[int]] = [[1, 2], [3, 4]]\nlet v: int = m[0][1]")
    
    def test_valid_index_write(self):
        """Valid: write to list element."""
        analyze("let x: [int] = [1, 2, 3]\nx[0] = 10")
    
    def test_valid_nested_index_write(self):
        """Valid: write to nested list element."""
        analyze("let m: [[int]] = [[1, 2], [3, 4]]\nm[0][1] = 99")
    
    def test_valid_index_with_variable(self):
        """Valid: index with variable."""
        analyze("let i: int = 0\nlet x: [int] = [1, 2, 3]\nlet y: int = x[i]")


# =============================================================================
# Semantic Tests: Error E0501 (index must be int)
# =============================================================================

class TestSemanticE0501:
    """Test E0501: list index must be int."""
    
    def test_error_index_string(self):
        """E0501: string index."""
        with pytest.raises(SemanticError) as exc:
            analyze('let x: [int] = [1, 2, 3]\nlet y: int = x["a"]')
        assert exc.value.code == "E0501"
        assert "int" in exc.value.message
    
    def test_error_index_float(self):
        """E0501: float index."""
        with pytest.raises(SemanticError) as exc:
            analyze("let x: [int] = [1, 2, 3]\nlet y: int = x[1.5]")
        assert exc.value.code == "E0501"
    
    def test_error_index_bool(self):
        """E0501: bool index."""
        with pytest.raises(SemanticError) as exc:
            analyze("let x: [int] = [1, 2, 3]\nlet y: int = x[true]")
        assert exc.value.code == "E0501"


# =============================================================================
# Semantic Tests: Error E0502 (target must be list)
# =============================================================================

class TestSemanticE0502:
    """Test E0502: cannot index into non-list type."""
    
    def test_error_index_int(self):
        """E0502: index into int."""
        with pytest.raises(SemanticError) as exc:
            analyze("let x: int = 42\nlet y: int = x[0]")
        assert exc.value.code == "E0502"
        assert "non-list" in exc.value.message
    
    def test_error_index_str(self):
        """E0502: index into str."""
        with pytest.raises(SemanticError) as exc:
            analyze('let x: str = "hello"\nlet y: str = x[0]')
        assert exc.value.code == "E0502"
    
    def test_error_index_bool(self):
        """E0502: index into bool."""
        with pytest.raises(SemanticError) as exc:
            analyze("let x: bool = true\nlet y: bool = x[0]")
        assert exc.value.code == "E0502"


# =============================================================================
# Semantic Tests: Error E0503 (assignment type mismatch)
# =============================================================================

class TestSemanticE0503:
    """Test E0503: cannot assign wrong type to list element."""
    
    def test_error_assign_str_to_int_list(self):
        """E0503: assign str to int list."""
        with pytest.raises(SemanticError) as exc:
            analyze('let x: [int] = [1, 2, 3]\nx[0] = "hello"')
        assert exc.value.code == "E0503"
        assert "str" in exc.value.message
        assert "int" in exc.value.message
    
    def test_error_assign_int_to_str_list(self):
        """E0503: assign int to str list."""
        with pytest.raises(SemanticError) as exc:
            analyze('let x: [str] = ["a", "b"]\nx[0] = 42')
        assert exc.value.code == "E0503"
    
    def test_error_assign_bool_to_float_list(self):
        """E0503: assign bool to float list."""
        with pytest.raises(SemanticError) as exc:
            analyze("let x: [float] = [1.0, 2.0]\nx[0] = true")
        assert exc.value.code == "E0503"


# =============================================================================
# Code Generation Tests
# =============================================================================

class TestCodeGenIndex:
    """Test code generation for index operations."""
    
    def test_codegen_index_read(self):
        """Generate Python: x[0]"""
        code = generate("let x: [int] = [1, 2, 3]\nlet y: int = x[0]")
        assert "x = [1, 2, 3]" in code
        assert "y = x[0]" in code
    
    def test_codegen_nested_index_read(self):
        """Generate Python: m[0][1]"""
        code = generate("let m: [[int]] = [[1, 2], [3, 4]]\nlet v: int = m[0][1]")
        assert "m = [[1, 2], [3, 4]]" in code
        assert "v = m[0][1]" in code
    
    def test_codegen_index_write(self):
        """Generate Python: x[0] = 10"""
        code = generate("let x: [int] = [1, 2, 3]\nx[0] = 10")
        assert "x[0] = 10" in code
    
    def test_codegen_nested_index_write(self):
        """Generate Python: m[0][1] = 99"""
        code = generate("let m: [[int]] = [[1, 2], [3, 4]]\nm[0][1] = 99")
        assert "m[0][1] = 99" in code


# =============================================================================
# Integration Tests (E2E)
# =============================================================================

class TestIntegrationIndex:
    """End-to-end tests with execution."""
    
    def test_e2e_read_first_element(self):
        """Read first element of list."""
        output = execute("let x: [int] = [10, 20, 30]\nprint(x[0])")
        assert output.strip() == "10"
    
    def test_e2e_read_last_element(self):
        """Read last element of list."""
        output = execute("let x: [int] = [10, 20, 30]\nprint(x[2])")
        assert output.strip() == "30"
    
    def test_e2e_modify_element(self):
        """Modify list element and print."""
        output = execute("let x: [int] = [1, 2, 3]\nx[1] = 99\nprint(x[0], x[1], x[2])")
        assert output.strip() == "1 99 3"
    
    def test_e2e_nested_read(self):
        """Read from nested list."""
        output = execute("let m: [[int]] = [[1, 2], [3, 4]]\nprint(m[1][0])")
        assert output.strip() == "3"
    
    def test_e2e_nested_modify(self):
        """Modify nested list element."""
        output = execute("let m: [[int]] = [[1, 2], [3, 4]]\nm[0][1] = 99\nprint(m[0][0], m[0][1])")
        assert output.strip() == "1 99"
    
    def test_e2e_index_with_expression(self):
        """Index with arithmetic expression."""
        output = execute("let x: [int] = [10, 20, 30]\nlet i: int = 1\nprint(x[i + 1])")
        assert output.strip() == "30"
    
    def test_e2e_swap_elements(self):
        """Swap two elements in list."""
        source = """
let x: [int] = [1, 2, 3]
let tmp: int = x[0]
x[0] = x[2]
x[2] = tmp
print(x[0], x[1], x[2])
"""
        output = execute(source)
        assert output.strip() == "3 2 1"
    
    def test_e2e_string_list_indexing(self):
        """Index into string list."""
        output = execute('let names: [str] = ["alice", "bob"]\nprint(names[1])')
        assert output.strip() == "bob"

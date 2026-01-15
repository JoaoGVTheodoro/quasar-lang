"""
Phase 8.3 Tests: Nested Structs & Integration

Tests complex struct composition: nesting, arrays, and function passing.
"""
import pytest
from quasar.parser.parser import Parser
from quasar.lexer.lexer import Lexer
from quasar.semantic.analyzer import SemanticAnalyzer
from quasar.codegen.generator import CodeGenerator
from quasar.semantic.errors import SemanticError


def parse(source):
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    return parser.parse()


def analyze(source):
    program = parse(source)
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)


def generate(source):
    program = analyze(source)
    generator = CodeGenerator()
    return generator.generate(program)


# ============================================================================
# Scenario 1: Nested Structs (Struct inside Struct)
# ============================================================================

def test_nested_struct_decl():
    """Declaring a struct with struct field."""
    source = """
    struct Point { x: int, y: int }
    struct Line { start: Point, finish: Point }
    """
    program = analyze(source)
    assert len(program.declarations) == 2


def test_nested_struct_init():
    """Instantiating nested structs."""
    source = """
    struct Point { x: int, y: int }
    struct Line { start: Point, finish: Point }
    
    let p1: Point = Point { x: 0, y: 0 }
    let p2: Point = Point { x: 10, y: 10 }
    let line: Line = Line { start: p1, finish: p2 }
    """
    program = analyze(source)
    assert len(program.declarations) == 5


def test_nested_struct_deep_read():
    """Deep member access: line.end.x"""
    source = """
    struct Point { x: int, y: int }
    struct Line { start: Point, finish: Point }
    
    let p1: Point = Point { x: 0, y: 0 }
    let p2: Point = Point { x: 10, y: 10 }
    let line: Line = Line { start: p1, finish: p2 }
    let val: int = line.finish.x
    """
    program = analyze(source)
    assert len(program.declarations) == 6


def test_nested_struct_deep_write():
    """Deep member write: line.finish.x = 99"""
    source = """
    struct Point { x: int, y: int }
    struct Line { start: Point, finish: Point }
    
    let p1: Point = Point { x: 0, y: 0 }
    let p2: Point = Point { x: 10, y: 10 }
    let line: Line = Line { start: p1, finish: p2 }
    line.finish.x = 99
    """
    program = analyze(source)
    assert len(program.declarations) == 6


# ============================================================================
# Scenario 2: Arrays of Structs
# ============================================================================

def test_array_of_structs_decl():
    """Declaring an array of structs."""
    source = """
    struct User { id: int }
    let users: [User] = [User { id: 1 }, User { id: 2 }]
    """
    program = analyze(source)
    assert len(program.declarations) == 2


def test_array_of_structs_index_member():
    """Index + member: users[0].id"""
    source = """
    struct User { id: int }
    let users: [User] = [User { id: 1 }, User { id: 2 }]
    let uid: int = users[0].id
    """
    program = analyze(source)
    assert len(program.declarations) == 3


def test_array_of_structs_in_loop():
    """Iterating over array of structs."""
    source = """
    struct User { id: int }
    let users: [User] = [User { id: 1 }, User { id: 2 }]
    for u in users {
        print(u.id)
    }
    """
    program = analyze(source)
    assert len(program.declarations) == 3


# ============================================================================
# Scenario 3: Struct with Array Field
# ============================================================================

def test_struct_with_array_field():
    """Struct containing an array field."""
    source = """
    struct User { id: int }
    struct Group { name: str, members: [User] }
    
    let g: Group = Group { 
        name: "Admins", 
        members: [User { id: 1 }, User { id: 2 }] 
    }
    """
    program = analyze(source)
    assert len(program.declarations) == 3


def test_struct_array_field_access():
    """Accessing array field then indexing."""
    source = """
    struct User { id: int }
    struct Group { name: str, members: [User] }
    
    let g: Group = Group { 
        name: "Admins", 
        members: [User { id: 42 }] 
    }
    let first_id: int = g.members[0].id
    """
    program = analyze(source)
    assert len(program.declarations) == 4


# ============================================================================
# Scenario 4: Passing Structs to Functions
# ============================================================================

def test_struct_as_function_param():
    """Structs can be passed to functions."""
    source = """
    struct Point { x: int, y: int }
    
    fn get_x(p: Point) -> int {
        return p.x
    }
    
    let pt: Point = Point { x: 5, y: 10 }
    let result: int = get_x(pt)
    """
    program = analyze(source)
    assert len(program.declarations) == 4


def test_struct_return_from_function():
    """Functions can return structs."""
    source = """
    struct Point { x: int, y: int }
    
    fn origin() -> Point {
        return Point { x: 0, y: 0 }
    }
    
    let o: Point = origin()
    """
    program = analyze(source)
    assert len(program.declarations) == 3


# ============================================================================
# Code Generation Tests
# ============================================================================

def test_codegen_nested_access():
    """Generated Python supports chained dot access."""
    source = """
    struct Point { x: int, y: int }
    struct Line { start: Point, finish: Point }
    
    let p1: Point = Point { x: 0, y: 0 }
    let p2: Point = Point { x: 10, y: 10 }
    let line: Line = Line { start: p1, finish: p2 }
    let val: int = line.finish.x
    """
    code = generate(source)
    assert "line.finish.x" in code


def test_codegen_array_struct_index():
    """Generated Python supports array[i].field"""
    source = """
    struct User { id: int }
    let users: [User] = [User { id: 1 }]
    let uid: int = users[0].id
    """
    code = generate(source)
    assert "users[0].id" in code

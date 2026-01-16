"""
Phase 13.2 Env API Hardening Tests

Covers Env static object hardening and defensive copy.
"""
import pytest
from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator

def analyze(source: str):
    lexer = Lexer(source)
    program = Parser(lexer.tokenize()).parse()
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)

def generate(source: str) -> str:
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    SemanticAnalyzer().analyze(ast)
    return CodeGenerator().generate(ast)

def compile_and_run(source: str, extra_globals: dict = None) -> dict:
    code = generate(source)
    exec_globals = {"__builtins__": __builtins__}
    if extra_globals:
        exec_globals.update(extra_globals)
    exec_locals = {}
    exec(code, exec_globals, exec_locals)
    return exec_locals

class TestEnvHardening:
    def test_env_namespace_shadowing(self):
        """let sys: str = 'x'; Env.args() should not crash."""
        source = """
let sys: str = "x"
let args: [str] = Env.args()
"""
        result = compile_and_run(source)
        assert isinstance(result["args"], list)
        assert all(isinstance(x, str) for x in result["args"])

    def test_env_args_defensive_copy(self):
        """Mutating Env.args() return value should not affect subsequent calls."""
        source = """
let a: [str] = Env.args()
a.push("MUTATED")
let b: [str] = Env.args()
"""
        result = compile_and_run(source)
        assert "MUTATED" in result["a"]
        assert "MUTATED" not in result["b"]

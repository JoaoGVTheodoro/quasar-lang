import os
import sys
import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator


def generate(source: str) -> str:
    """Helper to parse and generate Python code from Quasar source."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    SemanticAnalyzer().analyze(ast)
    return CodeGenerator().generate(ast)


def compile_and_run(source: str, mock_argv: list = None) -> tuple:
    """Compile Quasar to Python and execute, returning (stdout, stderr, returncode, py_code)."""
    py_code = generate(source)
    import tempfile
    import subprocess

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(py_code)
        py_path = f.name

    try:
        env = None
        cmd = [sys.executable, py_path]
        # If mock_argv provided, inject via environment variable trick by making a small wrapper
        if mock_argv is not None:
            # We'll run the generated code in-process instead to set sys.argv reliably
            # This path is used by some tests below; but for others we'll run subprocess
            import runpy
            original_argv = sys.argv
            try:
                sys.argv = mock_argv
                # Execute the compiled code and capture printed output
                import io
                import contextlib
                buf_out = io.StringIO()
                buf_err = io.StringIO()
                with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                    runpy.run_path(py_path, run_name="__main__")
                return buf_out.getvalue(), buf_err.getvalue(), 0, py_code
            finally:
                sys.argv = original_argv
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
            return result.stdout, result.stderr, result.returncode, py_code
    finally:
        os.remove(py_path)

def test_namespace_attack_os():
    code = '''
    let os: int = 0
    print(File.exists("/"))
    '''
    out, err, code_, py = compile_and_run(code)
    assert "True" in out or "False" in out
    assert "_q_os" in py
    assert "import os as _q_os" in py

def test_namespace_attack_sys():
    code = '''
    let sys: str = "fail"
    print(Env.args())
    '''
    # Run with a known argv to avoid depending on test runner's argv
    mock = ["script.py", "arg1"]
    out, err, code_, py = compile_and_run(code, mock_argv=mock)
    # argv[0] may be normalized to the real script path by runpy; check a stable argv entry
    assert "arg1" in out
    assert "_q_sys" in py
    assert "import sys as _q_sys" in py

def test_argv_isolation():
    code = '''
    let args: [str] = Env.args()
    args.push("extra")
    print(args)
    '''
    mock = ["script.py"]
    out, err, code_, py = compile_and_run(code, mock_argv=mock)
    # Should not error, and should include 'extra' in output
    assert "extra" in out
    # Codegen must use list(_q_sys.argv)
    assert "list(_q_sys.argv)" in py

def test_codegen_import_alias():
    code = '''
    print(File.exists("/"))
    print(Env.args())
    '''
    py = generate(code)
    assert "import os as _q_os" in py
    assert "import sys as _q_sys" in py
    assert "_q_os.path.exists" in py
    assert "list(_q_sys.argv)" in py

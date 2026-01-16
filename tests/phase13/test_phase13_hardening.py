import os
import sys
import tempfile

import pytest

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator


def generate(source: str) -> str:
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    SemanticAnalyzer().analyze(ast)
    return CodeGenerator().generate(ast)


def compile_and_run(source: str, mock_argv: list = None) -> tuple:
    py_code = generate(source)
    import tempfile
    import subprocess
    import runpy

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(py_code)
        py_path = f.name

    try:
        if mock_argv is not None:
            original_argv = sys.argv
            try:
                sys.argv = mock_argv
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
            result = subprocess.run([sys.executable, py_path], capture_output=True, text=True)
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
    mock = ["script.py", "arg1"]
    out, err, code_, py = compile_and_run(code, mock_argv=mock)
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
    assert "extra" in out
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

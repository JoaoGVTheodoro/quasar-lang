"""
Quasar CLI — Command Line Interface.

Provides commands for compiling, running, and checking Quasar source files.

Usage:
    quasar compile <file.qsr>   Compile to Python
    quasar run <file.qsr>       Compile and execute
    quasar check <file.qsr>     Validate without generating code
    quasar --version            Show version
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Version info
__version__ = "1.6.0"
__codename__ = "entropy"


# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="quasar",
        description="Quasar Programming Language Compiler",
        epilog="For more information, visit: https://github.com/JoaoGVTheodoro/quasar-lang",
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"Quasar {__version__} {__codename__}",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # compile command
    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile a Quasar file to Python",
    )
    compile_parser.add_argument(
        "file",
        type=str,
        help="Quasar source file (.qsr)",
    )
    compile_parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output file path (default: <input>.py)",
    )
    
    # run command
    run_parser = subparsers.add_parser(
        "run",
        help="Compile and execute a Quasar file",
    )
    run_parser.add_argument(
        "file",
        type=str,
        help="Quasar source file (.qsr)",
    )
    
    # check command
    check_parser = subparsers.add_parser(
        "check",
        help="Validate a Quasar file without generating code",
    )
    check_parser.add_argument(
        "file",
        type=str,
        help="Quasar source file (.qsr)",
    )
    
    return parser


def read_source(filepath: str) -> str:
    """
    Read source code from a file.
    
    Args:
        filepath: Path to the source file.
        
    Returns:
        Source code as string.
        
    Raises:
        SystemExit: If file not found or cannot be read.
    """
    path = Path(filepath)
    
    if not path.exists():
        print(f"error: file not found: {filepath}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    
    if not path.suffix == ".qsr":
        print(f"warning: expected .qsr extension, got '{path.suffix}'", file=sys.stderr)
    
    try:
        return path.read_text(encoding="utf-8")
    except IOError as e:
        print(f"error: cannot read file: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)


def compile_source(source: str, filename: str = "<stdin>") -> str:
    """
    Compile Quasar source to Python.
    
    Args:
        source: Quasar source code.
        filename: Source filename for error messages.
        
    Returns:
        Generated Python code.
        
    Raises:
        SystemExit: On compilation error.
    """
    # Import here to avoid circular imports and keep startup fast
    from quasar.lexer import Lexer
    from quasar.lexer.errors import LexerError
    from quasar.parser import Parser
    from quasar.parser.errors import ParserError
    from quasar.semantic import SemanticAnalyzer
    from quasar.semantic.errors import SemanticError
    from quasar.codegen import CodeGenerator
    
    try:
        # Lexical analysis
        lexer = Lexer(source, filename)
        tokens = lexer.tokenize()
        
        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Semantic analysis
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        # Code generation
        generator = CodeGenerator()
        return generator.generate(ast)
        
    except LexerError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    except ParserError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    except SemanticError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)


def check_source(source: str, filename: str = "<stdin>") -> bool:
    """
    Validate Quasar source without generating code.
    
    Args:
        source: Quasar source code.
        filename: Source filename for error messages.
        
    Returns:
        True if valid, exits on error.
    """
    # Import here to avoid circular imports
    from quasar.lexer import Lexer
    from quasar.lexer.errors import LexerError
    from quasar.parser import Parser
    from quasar.parser.errors import ParserError
    from quasar.semantic import SemanticAnalyzer
    from quasar.semantic.errors import SemanticError
    
    try:
        lexer = Lexer(source, filename)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        return True
        
    except LexerError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    except ParserError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    except SemanticError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)


def cmd_compile(args: argparse.Namespace) -> int:
    """
    Handle the 'compile' command.
    
    Compiles a Quasar file to Python and writes the output.
    """
    source = read_source(args.file)
    python_code = compile_source(source, args.file)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(args.file).with_suffix(".py")
    
    try:
        output_path.write_text(python_code, encoding="utf-8")
        print(f"✓ Compiled: {args.file} → {output_path}")
        return EXIT_SUCCESS
    except IOError as e:
        print(f"error: cannot write output: {e}", file=sys.stderr)
        return EXIT_ERROR


def cmd_run(args: argparse.Namespace) -> int:
    """
    Handle the 'run' command.
    
    Compiles a Quasar file and executes the generated Python code.
    """
    source = read_source(args.file)
    python_code = compile_source(source, args.file)
    
    # Execute the generated code
    try:
        exec(python_code, {"__name__": "__main__"})
        return EXIT_SUCCESS
    except Exception as e:
        print(f"runtime error: {e}", file=sys.stderr)
        return EXIT_ERROR


def cmd_check(args: argparse.Namespace) -> int:
    """
    Handle the 'check' command.
    
    Validates a Quasar file without generating code.
    """
    source = read_source(args.file)
    check_source(source, args.file)
    print(f"✓ Valid: {args.file}")
    return EXIT_SUCCESS


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for the Quasar CLI.
    
    Args:
        argv: Command line arguments (defaults to sys.argv[1:]).
        
    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if args.command is None:
        parser.print_help()
        return EXIT_SUCCESS
    
    if args.command == "compile":
        return cmd_compile(args)
    elif args.command == "run":
        return cmd_run(args)
    elif args.command == "check":
        return cmd_check(args)
    else:
        parser.print_help()
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())

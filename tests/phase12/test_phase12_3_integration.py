"""
Phase 12.3 Tests: Enum E2E Integration

End-to-end tests that compile and execute Quasar enum programs.
"""
import pytest
import subprocess

from quasar.lexer import Lexer
from quasar.parser import Parser
from quasar.semantic import SemanticAnalyzer
from quasar.codegen import CodeGenerator


def compile_quasar(source: str) -> str:
    """Compile Quasar source to Python code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    generator = CodeGenerator()
    return generator.generate(ast)


def execute_python(code: str) -> str:
    """Execute Python code and capture output."""
    result = subprocess.run(
        ["python", "-c", code],
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Python execution failed: {result.stderr}")
    return result.stdout


def compile_and_run(source: str) -> str:
    """Compile Quasar source and execute the result."""
    python_code = compile_quasar(source)
    return execute_python(python_code)


# ============================================================================
# Simple Enum E2E Tests
# ============================================================================

class TestEnumBasicE2E:
    """Basic enum functionality E2E tests."""

    def test_enum_decl_and_use(self):
        """Declare enum and use variant."""
        source = """
        enum Color { Red, Green, Blue }
        let c: Color = Color.Red
        print(c)
        """
        output = compile_and_run(source)
        assert "Color.Red" in output

    def test_enum_equality_true(self):
        """Enum equality returns True for same variant."""
        source = """
        enum Status { Ok, Err }
        let s: Status = Status.Ok
        print(s == Status.Ok)
        """
        output = compile_and_run(source)
        assert output.strip() == "True"

    def test_enum_equality_false(self):
        """Enum equality returns False for different variants."""
        source = """
        enum Status { Ok, Err }
        let s: Status = Status.Ok
        print(s == Status.Err)
        """
        output = compile_and_run(source)
        assert output.strip() == "False"

    def test_enum_inequality(self):
        """Enum inequality works."""
        source = """
        enum Light { Red, Green }
        print(Light.Red != Light.Green)
        """
        output = compile_and_run(source)
        assert output.strip() == "True"


# ============================================================================
# Enum in Control Flow E2E Tests
# ============================================================================

class TestEnumControlFlowE2E:
    """Enum in control flow structures."""

    def test_enum_in_if_true_branch(self):
        """Enum comparison takes true branch."""
        source = """
        enum State { On, Off }
        let s: State = State.On
        if s == State.On {
            print("enabled")
        } else {
            print("disabled")
        }
        """
        output = compile_and_run(source)
        assert output.strip() == "enabled"

    def test_enum_in_if_false_branch(self):
        """Enum comparison takes false branch."""
        source = """
        enum State { On, Off }
        let s: State = State.Off
        if s == State.On {
            print("enabled")
        } else {
            print("disabled")
        }
        """
        output = compile_and_run(source)
        assert output.strip() == "disabled"

    def test_enum_chain_conditions(self):
        """Multiple enum conditions."""
        source = """
        enum Priority { Low, Medium, High }
        let p: Priority = Priority.Medium
        if p == Priority.High {
            print("urgent")
        } else {
            if p == Priority.Medium {
                print("normal")
            } else {
                print("low")
            }
        }
        """
        output = compile_and_run(source)
        assert output.strip() == "normal"


# ============================================================================
# Enum with Functions E2E Tests
# ============================================================================

class TestEnumFunctionsE2E:
    """Enum with function parameters and returns."""

    def test_enum_function_param(self):
        """Pass enum to function."""
        source = """
        enum Status { Ok, Err }
        fn is_ok(s: Status) -> bool {
            return s == Status.Ok
        }
        print(is_ok(Status.Ok))
        print(is_ok(Status.Err))
        """
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines[0] == "True"
        assert lines[1] == "False"

    def test_enum_function_return(self):
        """Function returns enum."""
        source = """
        enum Result { Success, Failure }
        fn get_result(ok: bool) -> Result {
            if ok {
                return Result.Success
            }
            return Result.Failure
        }
        print(get_result(true))
        print(get_result(false))
        """
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert "Success" in lines[0]
        assert "Failure" in lines[1]


# ============================================================================
# State Machine E2E Tests
# ============================================================================

class TestEnumStateMachineE2E:
    """State machine pattern using enums."""

    def test_traffic_light_state_machine(self):
        """Traffic light transitions."""
        source = """
        enum TrafficLight { Red, Yellow, Green }
        
        fn next_light(current: TrafficLight) -> TrafficLight {
            if current == TrafficLight.Red {
                return TrafficLight.Green
            }
            if current == TrafficLight.Green {
                return TrafficLight.Yellow
            }
            return TrafficLight.Red
        }
        
        let light: TrafficLight = TrafficLight.Red
        print("Start: Red")
        
        light = next_light(light)
        if light == TrafficLight.Green {
            print("After 1: Green")
        }
        
        light = next_light(light)
        if light == TrafficLight.Yellow {
            print("After 2: Yellow")
        }
        
        light = next_light(light)
        if light == TrafficLight.Red {
            print("After 3: Red")
        }
        """
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines[0] == "Start: Red"
        assert lines[1] == "After 1: Green"
        assert lines[2] == "After 2: Yellow"
        assert lines[3] == "After 3: Red"

    def test_connection_state_machine(self):
        """Connection state transitions."""
        source = """
        enum ConnectionState { Disconnected, Connecting, Connected, Error }
        
        fn connect(state: ConnectionState) -> ConnectionState {
            if state == ConnectionState.Disconnected {
                return ConnectionState.Connecting
            }
            if state == ConnectionState.Connecting {
                return ConnectionState.Connected
            }
            return state
        }
        
        let conn: ConnectionState = ConnectionState.Disconnected
        
        conn = connect(conn)
        print(conn == ConnectionState.Connecting)
        
        conn = connect(conn)
        print(conn == ConnectionState.Connected)
        """
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines[0] == "True"
        assert lines[1] == "True"


# ============================================================================
# Complex Program E2E Tests
# ============================================================================

class TestEnumComplexE2E:
    """Complex programs using enums."""

    def test_enum_counting(self):
        """Count specific enum values."""
        source = """
        enum Vote { Yes, No, Abstain }
        
        fn count_yes(v1: Vote, v2: Vote, v3: Vote) -> int {
            let count: int = 0
            if v1 == Vote.Yes {
                count = count + 1
            }
            if v2 == Vote.Yes {
                count = count + 1
            }
            if v3 == Vote.Yes {
                count = count + 1
            }
            return count
        }
        
        print(count_yes(Vote.Yes, Vote.No, Vote.Yes))
        """
        output = compile_and_run(source)
        assert output.strip() == "2"

    def test_enum_with_loop(self):
        """Enum state with loop counter."""
        source = """
        enum ProcessState { Running, Stopping, Stopped }
        
        let state: ProcessState = ProcessState.Running
        let count: int = 0
        
        while state == ProcessState.Running {
            count = count + 1
            if count >= 3 {
                state = ProcessState.Stopping
            }
        }
        
        print(count)
        print(state == ProcessState.Stopping)
        """
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines[0] == "3"
        assert lines[1] == "True"

    def test_multiple_enums_together(self):
        """Multiple enum types in same program."""
        source = """
        enum Color { Red, Green, Blue }
        enum Size { Small, Medium, Large }
        
        let color: Color = Color.Blue
        let size: Size = Size.Medium
        
        if color == Color.Blue {
            print("color is blue")
        }
        
        if size == Size.Medium {
            print("size is medium")
        }
        """
        output = compile_and_run(source)
        lines = output.strip().split("\n")
        assert lines[0] == "color is blue"
        assert lines[1] == "size is medium"

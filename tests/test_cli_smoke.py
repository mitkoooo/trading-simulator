import subprocess
import sys
import os

CLI_LOOP_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "main.py")
)


def run_cli(commands: str):
    """Helper: run main.py with a sequence of newline-separated commands."""
    proc = subprocess.run(
        [sys.executable, CLI_LOOP_PATH],
        input=commands,
        text=True,
        capture_output=True,
        timeout=5.00,
    )

    assert proc.returncode == 0, f"CLI crashed: {proc.stderr!r}"
    return proc.stdout


def test_smoke_flow():
    cmds = "\n".join(["next", "buy AAPL 1 150.0", "status", "quit"]) + "\n"
    output = run_cli(cmds)

    assert "AAPL" in output
    assert "Cash balance:" in output
    assert "Pending" in output or "order" in output.lower()

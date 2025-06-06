import subprocess
import sys
import os

CLI_LOOP_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src", "main.py")
)


def run_cli(commands: str, tmp_path):
    """Helper: run main.py with a sequence of newline-separated commands."""
    proc = subprocess.run(
        [sys.executable, CLI_LOOP_PATH],
        input=commands,
        text=True,
        capture_output=True,
        timeout=5.00,
        cwd=str(tmp_path),
    )

    assert proc.returncode == 0, f"CLI crashed: {proc.stderr!r}"
    return proc.stdout


def test_smoke_flow(tmp_path):
    cmds = (
        "\n".join(
            [
                "next",
                "buy AAPL 1 150.0",
                "match AAPL",
                "status",
                "quit",
            ]
        )
        + "\n"
    )
    output = run_cli(cmds, tmp_path)

    # Basic CLI output checks
    assert "AAPL" in output
    assert "Cash balance:" in output
    assert "Order placed for AAPL." in output
    assert "TRADE: AAPL" in output or "TRADE: AAPL 1 @ $150.00" in output

    # Verify that logs went into tmp_path/trading.log, not project root
    log_file = tmp_path / "trading.log"
    assert log_file.exists()
    content = log_file.read_text()
    print(content)
    assert "NEXT command received" and "NEXT command processed" in content
    assert "BUY order queued: symbol=AAPL" in content
    assert "STATUS viewed:" in content

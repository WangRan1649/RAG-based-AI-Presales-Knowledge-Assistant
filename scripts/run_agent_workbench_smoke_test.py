"""Smoke test for Agent Workbench V2 demo and eval."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str]) -> None:
    print(f"\n$ {' '.join(command)}")
    completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout)
    if completed.stderr:
        print(completed.stderr)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    run_command(
        [
            sys.executable,
            "-m",
            "agent_workbench.harness.agent_orchestrator",
            "--question",
            "Can InsightFlow support private deployment and SLA?",
            "--no-trace",
        ]
    )
    run_command([sys.executable, "eval\\run_agent_eval.py"])
    print("\nSmoke test complete.")


if __name__ == "__main__":
    main()

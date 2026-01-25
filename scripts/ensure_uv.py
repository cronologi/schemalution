from __future__ import annotations

import platform
import shutil
import subprocess
import sys


def run(cmd: list[str]) -> int:
    return subprocess.run(cmd).returncode


def run_capture(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> int:
    if shutil.which("uv"):
        return 0

    if shutil.which("pipx"):
        print("uv not found; installing with pipx...", file=sys.stderr)
        code = run(["pipx", "install", "uv"])
        if code != 0:
            code = run(["pipx", "upgrade", "uv"])
        if code == 0 and shutil.which("uv"):
            return 0

    if platform.system() == "Darwin" and shutil.which("brew"):
        print("uv not found; installing with Homebrew...", file=sys.stderr)
        code = run(["brew", "install", "uv"])
        if code == 0 and shutil.which("uv"):
            return 0

    if platform.system() == "Windows" and shutil.which("winget"):
        print("uv not found; installing with winget...", file=sys.stderr)
        code = run(["winget", "install", "--id", "Astral.Uv", "-e"])
        if code == 0 and shutil.which("uv"):
            return 0

    print("uv not found; installing with pip --user...", file=sys.stderr)
    result = run_capture([sys.executable, "-m", "pip", "install", "--user", "uv"])
    if result.returncode != 0:
        stderr = result.stderr or ""
        if "externally-managed-environment" in stderr:
            print(
                "pip install blocked by PEP 668. Try one of:\n"
                "  - brew install uv\n"
                "  - pipx install uv\n"
                "  - uv installer: https://docs.astral.sh/uv/getting-started/installation/",
                file=sys.stderr,
            )
        else:
            print(stderr, file=sys.stderr)
        return result.returncode

    if not shutil.which("uv"):
        print(
            "uv installed, but not found on PATH. Ensure your user scripts directory is on PATH.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

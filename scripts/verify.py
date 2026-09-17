"""Cross-platform verification entry point. Use --full for Docker and browser checks."""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.path.abspath(Path(__file__).parent.parent))


def run(args: list[str], cwd: Path = ROOT, env: dict[str, str] | None = None) -> None:
    print(f"\n> {' '.join(args)}", flush=True)
    subprocess.run(args, cwd=cwd, env=env, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="Build Compose, test real sandbox, run E2E; needs Docker and installed Chromium",
    )
    args = parser.parse_args()
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise SystemExit("npm is required")
    python = sys.executable
    run([python, "-m", "ruff", "format", "--check", "."])
    run([python, "-m", "ruff", "check", "."])
    run([python, "-m", "mypy", "academy", "runner"])
    run([python, "scripts/validate_content.py"])
    run([python, "-m", "pytest", "-q", "-m", "not docker"])
    for command in ["lint", "typecheck", "test", "build"]:
        run([npm, "run", command], ROOT / "frontend")
    if args.full:
        run(["docker", "compose", "up", "--build", "-d", "--wait"])
        env = {
            **os.environ,
            "RUN_DOCKER_TESTS": "1",
            "E2E_URL": "http://127.0.0.1:" + os.getenv("ACADEMY_PORT", "8080"),
        }
        run([python, "-m", "pytest", "-q"], env=env)
        run([npm, "run", "e2e"], ROOT / "frontend", env=env)
    else:
        print(
            "\nLocal checks passed. Docker/security/E2E are not included; run --full before release."
        )


if __name__ == "__main__":
    main()

"""Only this trusted broker module talks to Docker. No host execution fallback."""

import json
import os
import shutil
import subprocess
import threading
import time
import uuid
from typing import Any

from runner.protocol import WorkerResponse

IMAGE = os.getenv("SANDBOX_IMAGE", "academy-sandbox:0.1.0")
OUTPUT_LIMIT = 512 * 1024
SLOTS = threading.BoundedSemaphore(2)


class RunnerUnavailable(RuntimeError):
    pass


def docker_command(name: str, timeout: int, memory: int) -> list[str]:
    return [
        "docker",
        "run",
        "--rm",
        "-i",
        "--name",
        name,
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--user=65534:65534",
        f"--memory={memory}m",
        f"--memory-swap={memory}m",
        "--cpus=1",
        "--pids-limit=32",
        "--ulimit",
        "nofile=64:64",
        "--ulimit",
        f"cpu={timeout}:{timeout + 1}",
        "--tmpfs=/tmp:rw,noexec,nosuid,size=32m,mode=1777",
        "--log-driver=none",
        "--env=OPENBLAS_NUM_THREADS=1",
        "--env=OMP_NUM_THREADS=1",
        "--env=MPLCONFIGDIR=/tmp/matplotlib",
        "--label=academy.sandbox=true",
        IMAGE,
    ]


def available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        return (
            subprocess.run(
                ["docker", "image", "inspect", IMAGE], capture_output=True, timeout=5
            ).returncode
            == 0
        )
    except (OSError, subprocess.TimeoutExpired):
        return False


def execute(payload: dict[str, Any], timeout: int = 10, memory: int = 256) -> dict[str, Any]:
    if not SLOTS.acquire(blocking=False):
        raise RunnerUnavailable("Runner занят. Повторите через несколько секунд.")
    name = "academy-" + uuid.uuid4().hex
    started = time.monotonic()
    process: subprocess.Popen | None = None
    chunks = bytearray()
    overflow = threading.Event()
    expired = False
    try:
        if not available():
            raise RunnerUnavailable(
                "Docker runner недоступен. Запустите Docker и соберите academy-sandbox:0.1.0."
            )
        process = subprocess.Popen(
            docker_command(name, timeout, memory),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        assert process.stdout is not None and process.stdin is not None

        def read_output() -> None:
            assert process is not None and process.stdout is not None
            while block := process.stdout.read(4096):
                remaining = OUTPUT_LIMIT - len(chunks)
                chunks.extend(block[: max(0, remaining)])
                if len(block) > remaining:
                    overflow.set()
                    # Keep draining (without retaining bytes) until the container is killed.
                    # A blocked docker attach pipe can otherwise block daemon cleanup.

        reader = threading.Thread(target=read_output, daemon=True)
        reader.start()

        def write_input() -> None:
            assert process is not None and process.stdin is not None
            try:
                process.stdin.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
                process.stdin.close()
            except (OSError, ValueError):
                pass  # Early worker exit is handled by its exit status / output below.

        writer = threading.Thread(target=write_input, daemon=True)
        writer.start()
        # Include Docker startup and blocked stdin in the monitored wall clock limit.
        deadline = started + timeout
        while process.poll() is None:
            if overflow.is_set() or time.monotonic() > deadline:
                expired = not overflow.is_set()
                break
            time.sleep(0.025)
        if expired or overflow.is_set():
            subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=10)
            process.kill()
        process.wait(timeout=10)
        reader.join(timeout=2)
        writer.join(timeout=2)
        if expired:
            result = {"error": "Timeout", "message": "Превышен лимит времени. Проверьте циклы."}
        elif overflow.is_set():
            result = {
                "error": "OutputLimit",
                "message": "Слишком большой вывод. Печатайте только небольшой preview.",
            }
        elif process.returncode == 137:
            result = {"error": "MemoryLimit", "message": "Превышен лимит памяти."}
        elif process.returncode in {125, 126, 127}:
            raise RunnerUnavailable("Docker не смог создать контейнер выполнения.")
        else:
            try:
                result = WorkerResponse.model_validate(
                    json.loads(bytes(chunks).decode("utf-8"))
                ).model_dump(exclude_none=True)
            except (ValueError, UnicodeError, RecursionError):
                result = {
                    "error": "ExecutionError",
                    "message": "Процесс завершился без корректного результата.",
                }
        return {**result, "duration": round(time.monotonic() - started, 3)}
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunnerUnavailable("Не удалось связаться с Docker runner.") from exc
    finally:
        if process is not None:
            try:
                subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=10)
            except (OSError, subprocess.TimeoutExpired):
                pass
            if process.poll() is None:
                process.kill()
            if process.stdout:
                process.stdout.close()
        SLOTS.release()

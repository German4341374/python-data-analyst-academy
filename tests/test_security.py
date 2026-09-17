import pytest

from runner.docker_executor import docker_command, execute


def test_sandbox_command_has_enforced_limits():
    command = docker_command("test", 3, 256)
    for flag in [
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--user=65534:65534",
        "--memory=256m",
        "--memory-swap=256m",
        "--pids-limit=32",
        "--cpus=1",
        "--log-driver=none",
    ]:
        assert flag in command
    assert not any("docker.sock" in x for x in command)
    assert not any(x in {"-v", "--volume", "--mount", "--privileged"} for x in command)


def run_code(code, timeout=6):
    return execute(
        {"kind": "playground", "function": "", "code": code, "data": []}, timeout=timeout
    )


@pytest.mark.docker
def test_infinite_loop_terminated(docker_ready):
    assert run_code("while True: pass", timeout=3)["error"] == "Timeout"


@pytest.mark.docker
def test_excessive_memory_terminated(docker_ready):
    result = run_code("data = bytearray(1024 * 1024 * 1024)")
    assert result["error"] in {"MemoryLimit", "MemoryError"}, result


@pytest.mark.docker
def test_huge_stdout_limited(docker_ready):
    result = run_code("print('x' * 50000)")
    assert result["error"] == "RuntimeError"
    assert len(result["stdout"]) <= 8192


@pytest.mark.docker
def test_raw_stdout_cannot_fill_host_memory(docker_ready):
    result = run_code("import os\nwhile True: os.write(1, b'x' * 4096)")
    assert result["error"] == "OutputLimit", result


@pytest.mark.docker
def test_network_unavailable(docker_ready):
    result = run_code("import socket\nsocket.create_connection(('1.1.1.1', 443), timeout=1)")
    assert result["error"] in {"OSError", "TimeoutError"}, result


@pytest.mark.docker
def test_no_host_mount_or_docker_socket(docker_ready):
    result = run_code(
        "import os\nassert not os.path.exists('/var/run/docker.sock')\nassert not os.path.exists('/host')\nassert os.getuid() == 65534\nopen('/app/forbidden', 'w').write('x')"
    )
    assert result["error"] in {"OSError", "PermissionError"}, result


@pytest.mark.docker
def test_process_abuse_limited(docker_ready):
    result = run_code(
        "import subprocess\nchildren = []\ntry:\n    for i in range(100):\n        children.append(subprocess.Popen(['sleep', '20']))\nexcept OSError:\n    print('PID_LIMIT', len(children))\nfinally:\n    for p in children: p.kill()",
        timeout=10,
    )
    assert "PID_LIMIT" in result.get("stdout", ""), result

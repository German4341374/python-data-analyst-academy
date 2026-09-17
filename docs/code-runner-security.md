# Runner threat model

Scope: current local Compose application, the trusted broker and the disposable learner worker. An independent fresh-context architecture review was performed; the implementation was then checked with real Docker abuse tests. This is a threat model and bounded control verification, not a claim of complete penetration testing.

## Overview and resources

| Resource | Actual configuration / authority | Evidence |
|---|---|---|
| Browser entry | Nginx published only on loopback, same-origin API | `compose.yaml`, `frontend/nginx.conf` |
| API | UID 10001, no Docker socket in Compose; owns sessions, references and progress | `Dockerfile`, `academy/api.py`, `academy/grading.py` |
| Database | PostgreSQL private network, named `postgres-data` volume; SQLite file in development | `compose.yaml`, `academy/db.py` |
| Broker | Private network, token checked with constant-time comparison; **root with Docker socket authority** | `runner/broker.py`, `Dockerfile`, `compose.yaml` |
| Learner image | Python scientific libraries and worker only; no reference functions or catalog | `runner/Dockerfile` |
| Learner job | Fresh non-root container, no network or mounts, read-only root, capabilities dropped, no-new-privileges | `runner/docker_executor.py::docker_command` |
| Resource controls | 1 CPU, 256 MiB by current catalog, no extra swap, 32 PIDs, 64 open files, 32 MiB tmpfs; per-case wall/CPU time | `docker_command`, content schema |
| Output boundary | 8,192-character Python streams; independent 512 KiB outer cap and validated result shapes | `runner/worker.py::LimitedWriter`, `runner/protocol.py`, `execute` |

## Boundaries and assumptions

The browser and submitted code are untrusted. In Compose the API sends an ID, code and case index to the broker; it cannot request arbitrary mounts, commands, images or limits. The broker resolves these from server-owned content. Each worker sees its own case, but no expected answer, session token, database credentials or host files. The trusted API computes references and compares the worker result. The worker cannot directly award progress.

The Python interpreter is deliberately unrestricted inside the container. A learner can import modules, inspect the worker, monkey-patch pandas, bypass Python stream wrappers, spawn subprocesses or emit forged JSON. Therefore the worker's `mutated` flag and result metadata are untrusted observations. The trusted protocol limits types, dimensions and message sizes, but it cannot prove that submitted code performed a legitimate computation. PNG validation checks encoding/signature, not a full image-decoder safety or dimension guarantee. Unknown verdict fields are discarded. Comparison against alternate expected outputs is independent of the worker.

Session cookies are HttpOnly/SameSite=Strict; secure-cookie mode is opt-in because the default endpoint is local HTTP. State-changing API calls require a custom header and cross-origin requests are not enabled. Nginx enforces body/rate limits; direct development API access does not inherit those Nginx controls. Passwords use Argon2 and session tokens are stored hashed. Content answers are intentionally revealable for learning. Public seeded fixtures are not secret exam material.

The Docker daemon, host kernel, base images, application content and broker code are trusted. Docker-socket access is effectively daemon/host authority; dropping broker Linux capabilities does not remove that authority. Local development places Docker-launcher authority in the API process; it still has no host execution fallback.

## Abuse scenarios and controls

| Scenario | Controls and residual risk | Priority |
|---|---|---|
| Infinite loop / allocation / process storm | Wall and CPU deadline, memory/PID limits, forced cleanup. Real tests exercise loop, 1 GiB allocation and child-process abuse | High for availability |
| Flood stdout, bypass `print` wrapper | Outer collector retains at most 512 KiB and keeps draining until termination, avoiding pipe deadlock. Raw `os.write` tested | High for availability |
| Read host secrets or contact network | No bind mounts, no socket, UID 65534, read-only root, network none. Tests check these cases; kernel escape remains possible | Critical if host boundary is broken |
| Forge success JSON / exploit result parser | Typed bounded envelope; trusted references/comparisons; malformed payload tests. Deliberate in-interpreter tampering and fixture memorization are not solved examination integrity | Medium for learning integrity |
| Leak hidden case via feedback | Only visible stdout, exception and output are returned; hidden feedback is categorical. Public repository still reveals generators | Medium for assessment integrity |
| Abuse Docker parameters / steal broker token | Fixed launch flags and catalog IDs, private network, no public broker port; token required. A broker compromise has very high impact | Critical for host authority |
| Many legitimate expensive submissions | Two execution slots in one broker process; Nginx throttling and API slots. No durable per-user budget, distributed queue or global multi-worker quota | High before public hosting |
| Broker crash during execution | `--rm`, timeout and finally cleanup cover ordinary paths. Cleanup command failures are best-effort and there is no independent orphan reaper | High before public hosting |

The wall deadline includes image availability checks, container startup and asynchronous stdin delivery. Each hidden case starts fresh, so a submission can consume several times the per-case limit. Cleanup uses separate bounded Docker calls; total request time can exceed the learner execution limit. If the daemon is unavailable the API reports unavailability and awards no progress.

## Severity calibration and deployment gate

Availability failures in the intended single-user localhost deployment are recoverable service interruptions. The same defects can become high severity on shared infrastructure. Docker-socket exposure, arbitrary mount/image control, a host-execution fallback or a demonstrated container escape would be critical boundary violations. Content answer exposure is lower severity here because explicit solutions and public fixtures are intentional; it becomes material if the platform is repurposed for certification.

Before shared hosting: separate runner infrastructure from application/database hosts; introduce authenticated durable quotas and an independent orphan reaper; provision unique secrets and TLS; pin/review images, monitor daemon/runtime updates; validate retention and recovery; review PNG/array parsing and adversarial grading; consider a stronger isolation layer. No such production readiness is claimed in v0.1.

Control references: [Docker resource constraints](https://docs.docker.com/engine/containers/resource_constraints/), [Docker engine security](https://docs.docker.com/engine/security/). Test commands and actual results are recorded in [verification.md](verification.md).

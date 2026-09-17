# Security policy

v0.1 is intended for local evaluation. This project executes untrusted Python in disposable Docker containers. Never execute learner code in the API process, expose the runner broker, mount the Docker socket into a learner container, or add a host-execution fallback.

Read [the threat model](docs/code-runner-security.md). The private broker has Docker-daemon authority. Host kernel/container-runtime vulnerabilities, privileged broker compromise and operational exhaustion remain relevant risks. Current tests demonstrate specific controls; they are not a sandbox-escape audit.

Do not post credentials, personal data, or a working host-compromise exploit in a public issue. Use the repository's private vulnerability reporting mechanism if enabled. Otherwise request a private contact channel through the maintainer's GitHub profile without including exploit details. Report the commit, environment, minimal reproduction, affected trust boundary and observed impact. No response-time SLA is promised.

Keep Docker/host components updated. Shared deployment requires unique secrets, HTTPS/secure cookies, a dedicated execution host, durable quotas/cleanup/monitoring and appropriate retention/account-recovery policies. Demo credentials in Compose are explicitly local-development defaults.

# harness/adapters/secrets/env.py — env-var SecretsProvider.
#
# RESPONSIBILITY
#   Resolve `secret://<NAME>` references by reading the environment
#   variable `<NAME>`. Reference implementation suitable for dev and
#   for production deployments that inject secrets through the
#   environment (Kubernetes, ECS task definitions, systemd EnvironmentFile).
#
# WHAT TO IMPLEMENT
#   - EnvSecrets class implementing SecretsProvider:
#       name = "env"
#       Constructor takes optional `prefix: str | None`. When set, the
#       provider looks up `<prefix><NAME>` instead of `<NAME>` — useful
#       for namespacing in shared environments.
#
#       resolve(ref):
#         - Validate ref starts with "secret://"; raise ConfigError
#           otherwise with context (ref=<truncated>).
#         - Strip prefix, prepend optional namespace.
#         - Read os.environ. Missing or empty → ConfigError with the
#           variable name in the message (the NAME is not sensitive;
#           the VALUE is).
#         - Return the value verbatim.
#
# DO NOT
#   - Log the resolved value at any level. Log only the variable name
#     and the resolution outcome (success / missing).
#   - Fall back to other sources (.env file, /etc/secrets/, etc.). One
#     adapter, one source. Customers who want .env loading wrap their
#     process startup.
#
# ENTRY POINT
#   Registered under `harness.secrets` as `env`.

# harness/adapters/secrets/base.py — the SecretsProvider Protocol.
#
# RESPONSIBILITY
#   Define the single Protocol every secrets provider implements. The
#   reference env-var provider lives in env.py; production providers
#   (Vault, AWS KMS, GCP Secret Manager) live in harness-enterprise.
#
# WHAT TO IMPLEMENT
#   - SecretsProvider as a typing.Protocol:
#
#       class SecretsProvider(Protocol):
#           name: str  # adapter name (e.g. "env", "vault", "aws_kms")
#
#           def resolve(self, ref: str) -> str:
#               """Resolve a `secret://<name>` reference to its plaintext
#               value. Called by config/resolution.py during harness.yaml
#               load — NOT in the hot path.
#
#               Raises ConfigError when `ref` is not a valid secret URI
#               or the referenced secret cannot be found. Never returns
#               an empty string — empty means missing, and missing must
#               surface as a loud error.
#               """
#
#   - Reference shape: `secret://<name>` where <name> is opaque to the
#     harness — the provider interprets it (env var name, Vault path,
#     KMS key id, etc.).
#
# DO NOT
#   - Cache resolved secrets in the Protocol layer. Caching is per-
#     provider (some need rotation, some don't); the harness just calls
#     resolve().
#   - Add a `list()` or `exists()` method. Secrets are pulled by name
#     at config-load time, not enumerated.
#   - Log resolved values. Ever. Even at debug.

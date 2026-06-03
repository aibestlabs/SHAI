# harness/config/resolution.py — env-var and secret interpolation.
#
# RESPONSIBILITY
#   Walk a parsed YAML dict and replace two reference forms in STRING
#   VALUES (never in keys):
#     ${ENV_VAR}        →  os.environ["ENV_VAR"]
#     secret://<name>   →  SecretsProvider.resolve("secret://<name>")
#
#   Resolution happens AFTER yaml.safe_load and BEFORE pydantic
#   validation in config/loader.py. Validators then see fully resolved
#   strings.
#
# WHAT TO IMPLEMENT
#   - resolve_all(data: Any, *, secrets: SecretsProvider | None) -> Any
#       Recurse over dict / list / scalar. On strings:
#         1. Substitute every ${NAME} with os.environ[NAME]. Missing
#            env vars → ConfigError naming the missing variable.
#         2. If the remaining string equals exactly "secret://<name>",
#            resolve via the SecretsProvider. The result REPLACES the
#            string in place.
#         3. If the string contains "secret://" but is not exactly a
#            secret URI → ConfigError. Refuse to substring-replace
#            secret references — that path leads to accidental
#            concatenation bugs and leaked values.
#       Return the transformed structure (new dict/list, not mutated
#       in place — keeps the original for diagnostics).
#
#   - The SecretsProvider used here is the one configured in
#     harness.yaml itself. Bootstrap order: load YAML → resolve env
#     vars only → pydantic-validate the secrets section enough to
#     instantiate the SecretsProvider → re-resolve with secrets enabled.
#     OR: require the SecretsProvider class to be resolvable without
#     secrets in its own constructor args. PICK ONE. Document the
#     decision in docs/architecture.md.
#
# DO NOT
#   - Allow ${VAR:-default} or other shell-style fallbacks. Missing
#     references must fail. The whole point is no silent defaults.
#   - Interpolate in dict keys. Keys come from the schema, not the
#     environment.
#   - Log resolved secret values. Log the reference and outcome only.

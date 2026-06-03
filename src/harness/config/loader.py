# harness/config/loader.py — parse harness.yaml into a HarnessConfig.
#
# RESPONSIBILITY
#   Read a YAML file from disk, run env/secret resolution over its raw
#   string values, and validate the result against the pydantic schema.
#
# WHAT TO IMPLEMENT
#   - load_yaml(path: str | Path) -> HarnessConfig
#       1. Read the file. IOError → ConfigError with path context.
#       2. yaml.safe_load it. yaml.YAMLError → ConfigError.
#       3. Pass the raw dict to config.resolution.resolve_all to
#          interpolate ${ENV_VAR} and secret://name references in
#          string values. Raise ConfigError on missing references.
#       4. Construct HarnessConfig(**resolved). pydantic ValidationError
#          is wrapped in ConfigError with the offending field path.
#       5. Return the validated HarnessConfig.
#
#   - load_dict(data: dict, *, secrets: SecretsProvider | None = None) -> HarnessConfig
#       Same flow without the file read. Used by tests and by
#       programmatic configuration.
#
# WHAT load_yaml DOES NOT DO
#   - Instantiate adapters. Adapter construction happens in
#     core.harness.Harness.from_yaml after the config is loaded. Keep
#     these stages separate so config errors surface before adapter
#     init errors.
#   - Cache results. Each call reads the file. Tests and the CLI's
#     `harness validate` rely on this.
#
# DO NOT
#   - Use yaml.load (unsafe). Always yaml.safe_load.
#   - Log the raw config dict — it may contain ${SECRET_FOO} markers
#     pre-resolution. Log only the path being loaded and the validation
#     outcome.

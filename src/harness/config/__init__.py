# harness/config/__init__.py
#
# Package marker. The HarnessConfig pydantic model lives in schema.py,
# the YAML loader in loader.py, and env/secret interpolation in
# resolution.py. No re-exports — callers import from the specific module.

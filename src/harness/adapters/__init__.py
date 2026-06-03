# harness/adapters/__init__.py
#
# Package marker. The adapter resolver (discovery.py) and each
# adapter-kind subpackage live below this. Protocols live in their
# respective domain modules (e.g. tools/registry.py, policy/engine.py,
# audit/sink.py) — adapters/<kind>/base.py re-states them only when a
# subpackage convention makes it clearer. No re-exports here.

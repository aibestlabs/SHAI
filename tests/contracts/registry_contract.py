# tests/contracts/registry_contract.py
#
# RESPONSIBILITY
#   Conformance suite every ToolRegistry adapter must pass.
#
# WHAT TO IMPLEMENT
#   - class ToolRegistryContract:
#       registry_factory: ClassVar[Callable[[], ToolRegistry]]
#       Same pattern as the other contracts. Tests:
#
#       def test_register_then_get(self): ...
#       def test_register_idempotent_on_identical_tool(self): ...
#       def test_register_conflict_raises_config_error(self): ...
#       def test_get_unknown_raises_tool_not_registered(self): ...
#       def test_list_returns_all_registered(self): ...
#       def test_register_many_equivalent_to_loop(self): ...
#
# DO NOT
#   - Test persistence semantics. Memory loses state on restart; Redis
#     persists; central service persists. The contract does not specify
#     persistence — registration is assumed to happen at startup.

"""argument_policy — deterministic argument-level gate.

Two checks called by check_tool_call after tool lookup, before Layer 2.

  1. check_argument_rules  — evaluates ArgumentRule declarations on the tool.
                             First violation raises ArgumentViolationError.

  2. check_irreversibility — enforces the tool's blast-radius classification.
                             Raises IrreversibleActionError when blocked.

Both are pure deterministic code. No LLM, no scoring, no probability.
check_tool_call catches both errors and converts them to _deny().
"""
from __future__ import annotations

import logging
from typing import Any

from harness.core.context import AgentContext
from harness.core.errors import ArgumentViolationError, IrreversibleActionError
from harness.core.types import Irreversibility
from harness.tools.tool import Tool

log = logging.getLogger(__name__)


def check_argument_rules(
    tool: Tool,
    args: dict[str, Any],
    ctx: AgentContext,
) -> None:
    """Evaluate all ArgumentRules on the tool. No-op when tool has none.

    Raises ArgumentViolationError on the first violation.
    """
    for rule in tool.argument_rules:
        violation = rule.evaluate(args)
        if violation:
            log.warning(
                "argument rule violation",
                extra={
                    "op": "argument_rule",
                    "tool_name": tool.name,
                    "violation": violation,
                    **ctx.to_log_fields(),
                },
            )
            raise ArgumentViolationError(
                f"argument rule violation on '{tool.name}': {violation}",
                agent_id=ctx.agent_id,
                op="argument_rule",
            )


def check_irreversibility(tool: Tool, ctx: AgentContext) -> None:
    """Enforce the tool's irreversibility classification.

    REVERSIBLE   — always passes.
    SENSITIVE    — passes only if ctx.human_approved is True.
    IRREVERSIBLE — passes only if ctx.human_approved is True.

    Raises IrreversibleActionError when blocked.
    """
    tier = tool.irreversibility

    if tier == Irreversibility.REVERSIBLE:
        return

    if not ctx.human_approved:
        reason = (
            f"tool '{tool.name}' is {tier.value} and requires "
            f"human_approved=True on AgentContext"
        )
        log.warning(
            "irreversible action blocked",
            extra={
                "op": "irreversibility_gate",
                "tool_name": tool.name,
                "irreversibility": tier.value,
                **ctx.to_log_fields(),
            },
        )
        raise IrreversibleActionError(
            reason,
            agent_id=ctx.agent_id,
            op="irreversibility_gate",
        )

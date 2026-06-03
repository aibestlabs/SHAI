# harness/adapters/scanners/basic_injection.py — reference prompt-injection scanner.
#
# RESPONSIBILITY
#   Detect well-known textual prompt-injection patterns using a small,
#   curated pattern set. Ships with core to provide a baseline input
#   scanner. Production users with real prompt-injection threat models
#   plug in Lakera, Protect AI, or similar via harness-enterprise.
#
# WHAT TO IMPLEMENT
#   - BasicInjectionScanner class implementing the Scanner Protocol:
#       name = "basic_injection"
#       Constructor optional sensitivity setting (low | medium | high)
#       that scales which pattern set is active. Default = medium.
#
#   - Pattern categories (small, opinionated, documented inline):
#       instruction_override   high     "ignore previous instructions",
#                                       "disregard your prompt", etc.
#       role_hijack            high     "you are now …", "pretend you are …",
#                                       "act as DAN", etc.
#       exfil_request          medium   "print your system prompt",
#                                       "what are your instructions",
#                                       "repeat your rules"
#       tool_coercion          medium   "you must call <tool>",
#                                       "before answering, call …"
#       delimiter_smuggling    low      Encoded/zero-width characters that
#                                       break out of expected sections
#                                       (only at sensitivity=high)
#
#   - scan() returns ScanResult with one Finding per match. Like
#     regex_pii, detail must NOT include the matched text — category
#     is what audit consumers act on.
#
#   - redacted_text: None. Injection detection does not auto-rewrite —
#     the agent decides whether to refuse, sanitize, or escalate.
#
# DO NOT
#   - Try to catch every variant. This is a baseline, not a complete
#     defense. Customers with serious prompt-injection threats use
#     specialized ML-based scanners.
#   - Block on low-confidence patterns. False positives at this layer
#     are a UX disaster; prefer recall < precision tradeoffs.
#   - Build a separate model loader, weights bundle, or anything that
#     requires network access at runtime. Regex + literal strings only.
#
# ENTRY POINT
#   Registered under `harness.scanners` as `basic_injection`.

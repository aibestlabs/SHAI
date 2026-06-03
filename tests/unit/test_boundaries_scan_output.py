# tests/unit/test_boundaries_scan_output.py
#
# RESPONSIBILITY
#   Cover boundaries/scan_output.run. Largely parallel to
#   test_boundaries_scan_input.py.
#
# WHAT TO TEST
#   - Same matrix as scan_input: clean, blocking, disabled, scanner
#     error tolerance, block_at threshold.
#   - AuditEvent.boundary == "output_scan" for every emission.
#
# DO NOT
#   - Duplicate test bodies from scan_input. If a shared scan-pipeline
#     helper exists in boundaries/__init__.py, test it once there and
#     reduce these files to "boundary correctly delegates with the
#     right boundary name and scanner set."

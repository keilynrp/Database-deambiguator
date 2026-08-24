"""pytest plugin: capture node ID -> marker names during a --collect-only run.

Used by `backend_test_partitions.py audit-markers` (issue #293 fast-feedback
follow-up) so the marker histogram rides along in the SAME collection pass
that produces the exhaustive node ID list, instead of one extra
`pytest -m <marker> --collect-only` subprocess per taxonomy marker (6
category markers + "slow" = 7 additional full collections of backend/tests,
on top of the exhaustive one — 8 total per guard-job run).

Writes {node_id: [marker names]} as JSON to the path in
UKIP_MARKER_AUDIT_OUT once collection finishes. A no-op when that env var is
unset, so loading this plugin (e.g. via -p) never changes the outcome of any
other collect-only run, including the ones `verify` still runs unmodified.
"""
import json
import os


def pytest_collection_finish(session):
    out_path = os.environ.get("UKIP_MARKER_AUDIT_OUT")
    if not out_path:
        return
    data = {item.nodeid: sorted(m.name for m in item.iter_markers()) for item in session.items}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)

"""Sentinel for the CI partition-union guard (issue #293).

`scripts/backend_test_partitions.py verify` is what CI trusts to prove that
the parallel shards it runs cover every test the exhaustive suite would have
collected. That trust is only worth something if the guard actually fails
when a shard is short one test — this file proves it does, as a permanent,
fast, DB-free regression test rather than a one-off manual demonstration.

No fixtures, no DB, no FastAPI import: this exercises `verify_union()` in
isolation against synthetic node IDs, which is exactly what the `unit`
marker means in this repo's taxonomy.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from backend_test_partitions import partition, shard_of, verify_union  # noqa: E402

pytestmark = pytest.mark.unit


_FAKE_NODE_IDS = [f"backend/tests/test_fixture_{i}.py::test_case" for i in range(200)]


def test_shard_of_is_deterministic():
    ids = _FAKE_NODE_IDS
    assert [shard_of(nid, 6) for nid in ids] == [shard_of(nid, 6) for nid in ids]


def test_partition_union_covers_every_node_id_by_construction():
    shards = partition(_FAKE_NODE_IDS, num_shards=6)
    result = verify_union(_FAKE_NODE_IDS, shards)
    assert result.ok
    assert result.missing == set()
    assert result.extra == set()
    assert result.exhaustive_count == len(_FAKE_NODE_IDS)
    assert result.union_count == len(_FAKE_NODE_IDS)


def test_guard_fails_when_a_partition_is_missing_one_test():
    """The mutation/sentinel required by #293's evidence checklist.

    Deliberately drop one node ID from one shard's list — simulating a shard
    definition that silently omitted a test — and assert the guard notices.
    """
    shards = partition(_FAKE_NODE_IDS, num_shards=6)
    mutated = [list(shard) for shard in shards]

    non_empty = next(i for i, s in enumerate(mutated) if s)
    removed_id = mutated[non_empty].pop(0)

    result = verify_union(_FAKE_NODE_IDS, mutated)

    assert not result.ok
    assert result.missing == {removed_id}
    assert result.extra == set()


def test_guard_flags_a_stale_id_that_no_longer_exists_in_the_exhaustive_suite():
    """The inverse mutation: a shard file listing an ID that isn't collected
    anymore (e.g. a stale cached shard file after a test was renamed)."""
    shards = partition(_FAKE_NODE_IDS, num_shards=6)
    mutated = [list(shard) for shard in shards]
    mutated[0].append("backend/tests/test_renamed_away.py::test_ghost")

    result = verify_union(_FAKE_NODE_IDS, mutated)

    assert not result.ok
    assert result.extra == {"backend/tests/test_renamed_away.py::test_ghost"}


def test_intentional_duplicate_across_shards_is_counted_not_flagged_as_error():
    shards = partition(_FAKE_NODE_IDS, num_shards=6)
    mutated = [list(shard) for shard in shards]
    duplicate_id = mutated[1][0]
    mutated[0].append(duplicate_id)

    result = verify_union(_FAKE_NODE_IDS, mutated)

    assert result.ok
    assert result.overlap_count == 1

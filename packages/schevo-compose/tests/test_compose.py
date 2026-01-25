from __future__ import annotations

from datetime import datetime, timezone

from schevo_compose import (
    ComposeContext,
    Fragment,
    choose_newer,
    compose_root,
    deep_merge,
    merge_arrays_by_key,
)


def test_deep_merge_merges_nested_and_overwrites_scalars() -> None:
    base = {"a": {"b": 1}, "x": 1}
    patch = {"a": {"c": 2}, "x": 2}

    result = deep_merge(base, patch)

    assert result == {"a": {"b": 1, "c": 2}, "x": 2}
    assert base == {"a": {"b": 1}, "x": 1}


def test_merge_arrays_by_key_preserves_order_and_merges() -> None:
    base = [{"id": 1, "v": "a"}, {"id": 2, "v": "b"}]
    patch = [{"id": 2, "v": "b2"}, {"id": 3, "v": "c"}]

    result = merge_arrays_by_key(base, patch, key="id")

    assert [item["id"] for item in result] == [1, 2, 3]
    assert result[1]["v"] == "b2"


def test_choose_newer_handles_timestamp_cases() -> None:
    older = Fragment(
        schema_id="x",
        payload={},
        updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    newer = Fragment(
        schema_id="x",
        payload={"v": 2},
        updated_at=datetime(2024, 2, 1, tzinfo=timezone.utc),
    )
    no_ts = Fragment(schema_id="x", payload={"v": 3})

    assert choose_newer(older, newer) is newer
    assert choose_newer(older, no_ts) is older
    assert choose_newer(no_ts, newer) is newer
    assert choose_newer(no_ts, no_ts) is no_ts


def test_compose_root_merges_and_warns_on_duplicates() -> None:
    context = ComposeContext()
    older = Fragment(
        schema_id="crm.customer",
        payload={"name": "Ada", "shared": "a"},
        updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    newer = Fragment(
        schema_id="crm.customer",
        payload={"name": "Ada v2", "shared": "b"},
        updated_at=datetime(2024, 2, 1, tzinfo=timezone.utc),
    )
    fragment_b = Fragment(schema_id="crm.order", payload={"order_id": "o-1"})

    result = compose_root(
        [older, fragment_b, newer],
        root_schema_id="crm.root",
        context=context,
    )

    assert result["schema_id"] == "crm.root"
    assert result["schema_version"] == 1
    assert result["components"]["crm.customer"] == newer.payload
    assert result["components"]["crm.order"] == fragment_b.payload
    assert result["shared"] == "b"
    assert any("duplicate fragment" in warning for warning in context.warnings)
    assert context.applied == [
        "merged:crm.customer",
        "merged:crm.order",
        "merged:crm.customer",
    ]


def test_compose_root_merges_two_schemas_into_root() -> None:
    fragment_a = Fragment(schema_id="crm.customer", payload={"customer_id": "c-1"})
    fragment_b = Fragment(schema_id="crm.order", payload={"order_id": "o-1"})

    result = compose_root(
        [fragment_a, fragment_b],
        root_schema_id="crm.root",
    )

    assert result["schema_id"] == "crm.root"
    assert result["schema_version"] == 1
    assert result["components"]["crm.customer"] == {"customer_id": "c-1"}
    assert result["components"]["crm.order"] == {"order_id": "o-1"}

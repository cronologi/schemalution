from schevo_compose import (
    ComposeContext,
    Fragment,
    __version__,
    choose_newer,
    compose_root,
    deep_merge,
    merge_arrays_by_key,
)


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_public_api_exports() -> None:
    assert Fragment(schema_id="x", payload={}) is not None
    assert ComposeContext() is not None
    assert callable(deep_merge)
    assert callable(merge_arrays_by_key)
    assert callable(choose_newer)
    assert callable(compose_root)

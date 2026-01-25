from schevo_pack_example_crm import EXAMPLE_PACK, __version__


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_placeholder_constant() -> None:
    assert EXAMPLE_PACK == "example_crm"

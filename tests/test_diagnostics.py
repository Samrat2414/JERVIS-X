from core import diagnostics


def test_packaged_app_skips_source_file_checks(monkeypatch):
    monkeypatch.setattr(
        diagnostics.sys,
        "frozen",
        True,
        raising=False,
    )

    assert diagnostics.check_required_files() == []
    assert diagnostics.check_required_folders() == []
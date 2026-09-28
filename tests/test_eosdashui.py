"""Focused render tests for the MonsterUI EOSdash shell."""

from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from fasthtml.common import Div, to_xml

import akkudoktoreos.server.dash.admin as admin_module
from akkudoktoreos.server.dash.admin import Admin, AdminConfig
from akkudoktoreos.server.dash.components import Error, Page, Success
from akkudoktoreos.server.dash.theme import EOSDASH_SCRIPT, EOSDASH_STYLES


def test_page_uses_monsterui_navigation_and_theme_picker() -> None:
    html = to_xml(
        Page(
            "Plan",
            {
                "Plan": "/eosdash/plan",
                "Config": "/eosdash/configuration",
            },
            Div("page content"),
            Div("server status"),
            "/eosdash/footer",
        )
    )

    assert "eos-shell" in html
    assert "eos-header" in html
    assert "eos-nav-panel" in html
    assert "eos-sidebar" not in html
    assert "uk-nav-secondary" in html
    assert "eos-nav-link uk-active" in html
    assert "<uk-theme-switcher" in html
    assert 'id="page-content"' in html
    assert 'id="eos-page-loading"' in html
    assert 'data-uk-spinner="ratio: 2.5"' in html
    assert 'icon="loader-circle"' not in html
    assert 'hx-indicator="#eos-page-loading"' in html
    assert 'role="status"' in html
    assert 'src="data:image/png;base64,' in html
    assert "/eosdash/assets/icon.png" not in html


def test_upload_modal_is_closed_and_reset_after_htmx_response() -> None:
    configuration_source = (
        Path(__file__).parents[1] / "src" / "akkudoktoreos" / "server" / "dash" / "configuration.py"
    ).read_text(encoding="utf-8")
    script = to_xml(EOSDASH_SCRIPT)

    assert "data_eos_upload_form=True" in configuration_source
    assert "htmx:beforeSwap" in script
    assert "[data-eos-upload-form]" in script
    assert "form.reset()" in script
    assert "window.UIkit.modal(modal).hide()" in script


def test_admin_configuration_contains_export_delete_action() -> None:
    _, content = AdminConfig(
        "127.0.0.1",
        8503,
        None,
        {"general": {"config_file_path": "/data/EOS.config.json"}},
        {},
    )
    html = to_xml(Div(*content))

    assert "Delete file" in html
    assert 'name="selected_delete_file_name"' in html
    assert '"action": "delete_export_file"' in html
    assert "admin-delete-config-modal" not in html
    assert "The active EOS.config.json is never affected." in html
    assert "uk-btn-destructive" in html


def test_admin_delete_removes_only_selected_export(monkeypatch, tmp_path: Path) -> None:
    export_file = tmp_path / "eos_config_saved.json"
    export_file.write_text("{}", encoding="utf-8")
    active_config = tmp_path / "EOS.config.json"
    active_config.write_text('{"active": true}', encoding="utf-8")
    monkeypatch.setattr(admin_module, "export_import_directory", tmp_path)

    _, content = AdminConfig(
        "127.0.0.1",
        8503,
        {
            "category": "configuration",
            "action": "delete_export_file",
            "delete_file_name": export_file.name,
        },
        {"general": {"config_file_path": str(active_config)}},
        {},
    )
    html = to_xml(Div(*content))

    assert not export_file.exists()
    assert active_config.read_text(encoding="utf-8") == '{"active": true}'
    assert f"Deleted '{export_file.name}'" in html


def test_admin_delete_options_exclude_active_config(monkeypatch, tmp_path: Path) -> None:
    active_config = tmp_path / "EOS.config.json"
    active_config.write_text('{"active": true}', encoding="utf-8")
    export_file = tmp_path / "eos_config_saved.json"
    export_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(admin_module, "export_import_directory", tmp_path)

    _, content = AdminConfig(
        "127.0.0.1",
        8503,
        None,
        {"general": {"config_file_path": str(active_config)}},
        {},
    )
    soup = BeautifulSoup(to_xml(Div(*content)), "html.parser")
    import_options = [
        option.get_text(strip=True)
        for option in soup.select('select[name="selected_import_file_name"] option')
    ]
    delete_options = [
        option.get_text(strip=True)
        for option in soup.select('select[name="selected_delete_file_name"] option')
    ]

    assert active_config.name in import_options
    assert active_config.name not in delete_options
    assert export_file.name in delete_options


def test_admin_delete_rejects_active_config(monkeypatch, tmp_path: Path) -> None:
    active_config = tmp_path / "EOS.config.json"
    active_config.write_text('{"active": true}', encoding="utf-8")
    monkeypatch.setattr(admin_module, "export_import_directory", tmp_path)

    _, content = AdminConfig(
        "127.0.0.1",
        8503,
        {
            "category": "configuration",
            "action": "delete_export_file",
            "delete_file_name": active_config.name,
        },
        {"general": {"config_file_path": str(active_config)}},
        {},
    )

    assert active_config.exists()
    assert "not found in" in to_xml(Div(*content))


def test_admin_delete_rejects_file_outside_export_directory(monkeypatch, tmp_path: Path) -> None:
    export_directory = tmp_path / "exports"
    export_directory.mkdir()
    outside_file = tmp_path / "EOS.config.json"
    outside_file.write_text('{"active": true}', encoding="utf-8")
    monkeypatch.setattr(admin_module, "export_import_directory", export_directory)

    _, content = AdminConfig(
        "127.0.0.1",
        8503,
        {
            "category": "configuration",
            "action": "delete_export_file",
            "delete_file_name": "../EOS.config.json",
        },
        {"general": {"config_file_path": str(outside_file)}},
        {},
    )

    assert outside_file.exists()
    assert "not found in" in to_xml(Div(*content))


@pytest.mark.parametrize("category", ["cache", "configuration", "database"])
def test_admin_keeps_action_category_open(monkeypatch, category: str) -> None:
    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return self.payload

    def fake_get(url: str, timeout: int):
        payload = (
            {"general": {"config_file_path": "/data/EOS.config.json"}}
            if url.endswith("/v1/config")
            else {}
        )
        return FakeResponse(payload)

    monkeypatch.setattr(admin_module.requests, "get", fake_get)
    html = to_xml(Admin("127.0.0.1", 8503, {"category": category, "action": "none"}))
    soup = BeautifulSoup(html, "html.parser")

    for section_category in ("cache", "configuration", "database"):
        section = soup.select_one(f"#admin-{section_category}-section")
        assert section is not None
        assert section.has_attr("open") is (section_category == category)


def test_json_configuration_uses_a_save_action() -> None:
    configuration_source = (
        Path(__file__).parents[1] / "src" / "akkudoktoreos" / "server" / "dash" / "configuration.py"
    ).read_text(encoding="utf-8")

    assert '"Save JSON"' in configuration_source
    assert 'value="save_raw_config"' in configuration_source
    assert "data_json_error=True" in configuration_source
    assert '"Reset"' not in configuration_source


def test_readonly_configuration_toggle_has_explicit_spacing() -> None:
    configuration_source = (
        Path(__file__).parents[1] / "src" / "akkudoktoreos" / "server" / "dash" / "configuration.py"
    ).read_text(encoding="utf-8")
    styles = to_xml(EOSDASH_STYLES)

    assert 'cls="eos-config-readonly-toggle"' in configuration_source
    assert ".eos-config-readonly-toggle" in styles
    assert "gap: .625rem" in styles


def test_status_messages_use_frankenui_alert_markup() -> None:
    success = to_xml(Success("Saved"))
    error = to_xml(Error("Invalid JSON"))

    assert "uk-alert-success" in success
    assert "uk-alert-danger" in error
    assert 'role="alert"' in success
    assert 'role="alert"' in error


def test_dashboard_does_not_mix_daisyui_components() -> None:
    dash_dir = Path(__file__).parents[1] / "src" / "akkudoktoreos" / "server" / "dash"
    imports = "\n".join(path.read_text(encoding="utf-8") for path in dash_dir.glob("*.py"))

    assert "monsterui.daisy" not in imports


def test_local_monsterui_assets_are_packaged() -> None:
    assets = (
        Path(__file__).parents[1]
        / "src"
        / "akkudoktoreos"
        / "server"
        / "dash"
        / "assets"
        / "vendor"
    )

    assert (assets / "franken-core-2.0.0.min.css").is_file()
    assert (assets / "franken-core-2.0.0.iife.js").is_file()
    assert (assets / "franken-icon-2.0.0.iife.js").is_file()
    assert (assets / "tailwind-3.4.17.js").is_file()
    assert (assets / "LICENSE.franken-ui").is_file()
    assert (assets / "LICENSE.tailwindcss").is_file()

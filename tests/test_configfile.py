import json
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from akkudoktoreos.config.config import ConfigEOS, GeneralSettings


class TestConfigEOSToConfigFile:
    def test_to_config_file_writes_file(self, config_eos):
        config_path = config_eos.general.config_file_path

        # Remove file to test writing
        config_path.unlink(missing_ok=True)

        config_eos.to_config_file()

        assert config_path.exists()
        assert config_path.read_text().strip().startswith("{")

    def test_to_config_file_excludes_computed_fields(self, config_eos):
        config_path = config_eos.general.config_file_path

        config_eos.to_config_file()
        data = json.loads(config_path.read_text())

        assert "timezone" not in data["general"]
        assert "data_output_path" not in data["general"]
        assert "config_folder_path" not in data["general"]
        assert "config_file_path" not in data["general"]

    def test_to_config_file_excludes_defaults(self, config_eos):
        """Ensure fields with default values are excluded when saving config."""

        # Pick fields that have defaults
        default_latitude = GeneralSettings.model_fields["latitude"].default
        default_longitude = GeneralSettings.model_fields["longitude"].default

        # Ensure fields are at default values
        config_eos.general.latitude = default_latitude
        config_eos.general.longitude = default_longitude

        # Save the config using the correct path managed by config_eos
        config_eos.to_config_file()

        # Read back JSON from the correct path
        config_file_path = config_eos.general.config_file_path
        content = json.loads(config_file_path.read_text(encoding="utf-8"))

        # Default fields should not appear
        assert "latitude" not in content["general"]
        assert "longitude" not in content["general"]

        # Non-default value should appear
        config_eos.general.latitude = 48.0
        config_eos.to_config_file()
        content = json.loads(config_file_path.read_text(encoding="utf-8"))
        assert content["general"]["latitude"] == 48.0

    def test_to_config_file_excludes_none_fields(self, config_eos):
        config_eos.general.latitude = None

        config_path = config_eos.general.config_file_path
        config_eos.to_config_file()

        data = json.loads(config_path.read_text())

        assert "latitude" not in data["general"]

    def test_to_config_file_includes_version(tmp_path, config_eos):
        """Ensure general.version is always included."""
        # Save config
        config_eos.to_config_file()

        # Read back JSON
        config_file_path = config_eos.general.config_file_path
        content = json.loads(config_file_path.read_text(encoding="utf-8"))

        # Assert 'version' is included even if default
        assert content["general"]["version"] == config_eos.general.version

    def test_to_config_file_roundtrip(self, config_eos):
        config_eos.merge_settings_from_dict(
            {
                "general": {"latitude": 48.0},
                "server": {"port": 9000},
            }
        )

        config_path = config_eos.general.config_file_path
        config_eos.to_config_file()

        raw_data = json.loads(config_path.read_text())
        reloaded = ConfigEOS.model_validate(raw_data)

        assert reloaded.general.latitude == 48.0
        assert reloaded.server.port == 9000

    def test_replace_config_file_writes_file_and_reloads_settings(self, config_eos):
        config_path = config_eos.general.config_file_path
        assert config_path is not None
        original_content = config_path.read_text(encoding="utf-8")

        backup_path = config_eos.replace_config_file({"general": {"latitude": 48.0}})

        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.read_text(encoding="utf-8") == original_content
        assert config_eos.general.latitude == 48.0

        content = json.loads(config_path.read_text(encoding="utf-8"))
        assert content["general"]["latitude"] == 48.0
        assert content["general"]["version"] == config_eos.general.version
        assert "config_file_path" not in content["general"]

    def test_replace_config_file_rejects_non_object_json(self, config_eos):
        config_path = config_eos.general.config_file_path
        assert config_path is not None
        original_content = config_path.read_text(encoding="utf-8")

        with pytest.raises(TypeError):
            config_eos.replace_config_file(["not", "an", "object"])  # type: ignore[arg-type]

        assert config_path.read_text(encoding="utf-8") == original_content

    def test_replace_config_file_restores_original_on_write_error(self, config_eos):
        config_path = config_eos.general.config_file_path
        assert config_path is not None
        original_content = config_path.read_text(encoding="utf-8")

        with patch.object(Path, "write_text", side_effect=OSError("disk full")):
            with pytest.raises(OSError, match="disk full"):
                config_eos.replace_config_file({"general": {"latitude": 48.0}})

        assert config_path.read_text(encoding="utf-8") == original_content

    def test_delete_config_file_recreates_minimal_file_and_keeps_backup(self, config_eos):
        config_eos.merge_settings_from_dict({"general": {"latitude": 48.0}})
        config_eos.to_config_file()
        config_path = config_eos.general.config_file_path
        assert config_path is not None

        backup_path = config_eos.delete_config_file()

        assert backup_path is not None
        assert backup_path.exists()
        assert json.loads(backup_path.read_text(encoding="utf-8"))["general"]["latitude"] == 48.0
        assert config_path.exists()
        assert config_eos.general.latitude == GeneralSettings.model_fields["latitude"].default

        content = json.loads(config_path.read_text(encoding="utf-8"))
        assert content["general"]["version"] == config_eos.general.version
        assert "latitude" not in content["general"]


class TestConfigFileApi:
    @pytest.fixture
    def client(self, config_eos):
        from akkudoktoreos.server.eos import app

        return TestClient(app)

    def test_config_file_download_replace_and_delete(self, client, config_eos):
        response = client.get("/v1/config/file")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        assert json.loads(response.text)["general"]["version"] == config_eos.general.version

        response = client.post(
            "/v1/config/file",
            content=json.dumps({"general": {"latitude": 48.0}}),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 200
        replaced = response.json()
        assert replaced["action"] == "replace"
        assert replaced["backup_id"]
        assert replaced["configuration"]["general"]["latitude"] == 48.0

        response = client.delete("/v1/config/file")
        assert response.status_code == 200
        deleted = response.json()
        assert deleted["action"] == "delete"
        assert deleted["backup_id"]
        assert (
            deleted["configuration"]["general"]["latitude"]
            == GeneralSettings.model_fields["latitude"].default
        )

    def test_config_file_replace_rejects_invalid_json(self, client, config_eos):
        config_path = config_eos.general.config_file_path
        assert config_path is not None
        original_content = config_path.read_text(encoding="utf-8")

        response = client.post(
            "/v1/config/file",
            content="{invalid",
            headers={"content-type": "application/json"},
        )

        assert response.status_code == 400
        assert config_path.read_text(encoding="utf-8") == original_content

    def test_config_file_replace_accepts_multipart_upload(self, client):
        response = client.post(
            "/v1/config/file",
            files={"file": ("EOS.config.json", '{"general":{"latitude":48}}', "application/json")},
        )

        assert response.status_code == 200
        assert response.json()["configuration"]["general"]["latitude"] == 48.0

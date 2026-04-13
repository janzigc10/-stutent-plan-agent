from pathlib import Path

from app.config import Settings


def test_settings_loads_env_file_from_project_root() -> None:
    env_file = Settings.model_config.get("env_file")

    assert env_file == Path(__file__).resolve().parents[1] / ".env"
    assert Settings.model_config.get("env_file_encoding") == "utf-8"

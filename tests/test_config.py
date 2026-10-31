from pathlib import Path

from biteharbor.config import Settings


def test_settings_are_safe_without_api_key(tmp_path: Path):
    settings = Settings(_env_file=None, data_dir=tmp_path)
    assert settings.openai_api_key is None
    assert settings.max_tool_iterations == 5
    assert settings.data_dir == tmp_path

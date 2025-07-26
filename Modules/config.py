import json
from dataclasses import dataclass
from pathlib import Path
from platformdirs import user_config_dir

APP_NAME = "yt_ripa"  

CONFIG_DIR = Path(user_config_dir(APP_NAME))
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "Settings.json"

if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text("{}", encoding="utf-8")

with CONFIG_FILE.open("r", encoding="utf-8") as f:
    JsonConfig = json.load(f)

@dataclass
class Config:
    def __init__(self):
        self._youtube_api_key = JsonConfig.get("YOUTUBE_API_KEY", "")
        self._download_dir = JsonConfig.get("DOWNLOAD_DIR", str(Path.cwd() / "downloads"))
        self._group_by_artist = JsonConfig.get("GROUP_BY_ARTIST", True)
        self._group_by_album = JsonConfig.get("GROUP_BY_ALBUM", True)

    @property
    def youtube_api_key(self) -> str:
        return self._youtube_api_key

    @youtube_api_key.setter
    def youtube_api_key(self, new_key: str) -> None:
        self._youtube_api_key = new_key
        JsonConfig["YOUTUBE_API_KEY"] = new_key
        self._save_json()

    @property
    def download_dir(self) -> str:
        return self._download_dir

    @download_dir.setter
    def download_dir(self, new_path: str) -> None:
        self._download_dir = new_path
        JsonConfig["DOWNLOAD_DIR"] = new_path
        self._save_json()

    @property
    def group_by_artist(self) -> bool:
        return self._group_by_artist

    @group_by_artist.setter
    def group_by_artist(self, new_value: bool) -> None:
        self._group_by_artist = new_value
        JsonConfig["GROUP_BY_ARTIST"] = new_value
        self._save_json()

    @property
    def group_by_album(self) -> bool:
        return self._group_by_album

    @group_by_album.setter
    def group_by_album(self, new_value: bool) -> None:
        self._group_by_album = new_value
        JsonConfig["GROUP_BY_ALBUM"] = new_value
        self._save_json()

    def _save_json(self) -> None:
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(JsonConfig, f, indent=4)

CONFIG = Config()
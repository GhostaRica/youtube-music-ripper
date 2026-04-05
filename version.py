import requests
from packaging.version import Version

__version__ = "0.3.0"

GITHUB_USER = "GhostaRica"
REPO_NAME = "youtube-music-ripper"
API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/releases/latest"

def check_for_update() -> Version | None:
    r = requests.get(API_URL)
    if r.status_code != 200:
        return None

    latest_version = r.json()["tag_name"].lstrip("v")

    if not latest_version:
        return None
    
    if Version(latest_version) > Version(__version__):
        return latest_version

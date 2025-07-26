from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from classes.music.song import Song

class AlbumType(str, Enum):
    SINGLE = "Single"
    ALBUM = "Album"

@dataclass
class Album:
    title: str
    album_artist: str
    cover_url: Optional[str] = None
    album_type: AlbumType = AlbumType.ALBUM
    songs: List[Song] = field(default_factory=list)

    def add_song(self, song: Song):
        self.songs.append(song)
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from classes.music.song import Song

class AlbumType(str, Enum):
    SINGLE = "Single"
    ALBUM = "Album"

@dataclass
class Album:
    name: str = ""
    artist: str = ""
    cover_url: Optional[str] = None
    _type: AlbumType = AlbumType.ALBUM
    songs: List[Song] = field(default_factory=list)

    def add_song(self, song: Song):
        self.songs.append(song)

    def get_songs_count(self) -> int:
        return len(self.songs)

    def get_selected_songs(self) -> List[Song]:
        return [song for song in self.songs if song.selected]

    def get_selected_songs_count(self) -> List[Song]:
        return len([song for song in self.songs if song.selected])

    @property
    def type(self) -> AlbumType:
        if self.get_selected_songs_count() == 1:
            return AlbumType.SINGLE
        return self._type

    @type.setter
    def type(self, value: AlbumType):
        self._type = value

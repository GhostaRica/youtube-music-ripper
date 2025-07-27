from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Song:
    video_id: str = ""
    title: str = ""
    artists: List[str] = field(default_factory=list)
    duration: Optional[int] = None
    year: Optional[int] = None
    genres: List[str] = field(default_factory=list)
    track_number: int = 1
    selected: bool = True

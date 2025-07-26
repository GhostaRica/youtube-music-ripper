from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Song:
    title: str
    artists: List[str] = field(default_factory=list)
    duration_seconds: Optional[int] = None
    year: Optional[int] = None
    genres: List[str] = field(default_factory=list)
    track_number: Optional[int] = None

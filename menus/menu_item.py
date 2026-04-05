from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class MenuItem:
    id: str
    label: str
    value: Optional[Any] = None
    action: Optional[callable] = None
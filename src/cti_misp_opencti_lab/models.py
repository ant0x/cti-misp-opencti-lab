from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ObservableType = Literal["ipv4", "ipv6", "domain", "url", "md5", "sha1", "sha256", "email", "unknown"]


@dataclass(frozen=True)
class Observable:
    value: str
    type: ObservableType
    source: str = "manual"
    confidence: int = 50
    tlp: str = "TLP:CLEAR"
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def key(self) -> tuple[str, str]:
        return self.type, self.value


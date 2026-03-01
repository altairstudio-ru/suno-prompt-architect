from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class GenerationRequest:
    genre: str
    mood: str
    bpm: int
    energy: int                          # 1..5
    language: str = "ru"
    vocal_type: str = "male_baritone"
    structure: List[str] = field(default_factory=lambda: ["verse", "chorus"])
    lyrics: Optional[str] = None         # если передан — язык в style_prompt не добавляем
    references: List[str] = field(default_factory=list)
    overrides: dict = field(default_factory=dict)
    scenario: str = "single"             # single | album | ab_test

    def has_lyrics(self) -> bool:
        return self.lyrics is not None and self.lyrics.strip() != ""

    def is_instrumental(self) -> bool:
        return self.vocal_type == "no_vocal"

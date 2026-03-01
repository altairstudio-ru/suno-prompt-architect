from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class GenerationResponse:
    style_prompt: str
    lyrics_meta: List[str]
    reproducibility_hash: str
    warnings: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def char_count(self) -> int:
        return len(self.style_prompt)

    def is_valid(self) -> bool:
        return self.char_count() <= 200

    def format_lyrics_meta(self) -> str:
        return "\n".join(f"[{s.capitalize()}]" for s in self.lyrics_meta)

    def display(self) -> str:
        lines = [
            f"🎵 Style Prompt ({self.char_count()}/1000):",
            f"   {self.style_prompt}",
            f"",
            f"📋 Lyrics Meta:",
            f"{self.format_lyrics_meta()}",
            f"",
            f"🔑 Hash: {self.reproducibility_hash[:12]}...",
        ]
        if self.warnings:
            lines.append(f"⚠️  Warnings: {', '.join(self.warnings)}")
        return "\n".join(lines)

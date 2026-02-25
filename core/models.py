"""Input validation models — pure Python dataclasses (no Pydantic required)."""
from __future__ import annotations
from dataclasses import dataclass, field
from core.loader import valid_keys

MAX_INSTRUMENTS = 3
STYLE_LIMIT = 200


class ValidationError(Exception):
    """Raised when input fails validation."""
    pass


@dataclass
class PromptInput:
    genre: str
    mood: str
    tempo: str
    vocal_type: str
    energy: str | None = None
    instruments: list[str] = field(default_factory=list)
    production: str | None = None
    structure_hints: str | None = None

    def __post_init__(self):
        self._validate()

    def _validate(self):
        def check(val, dict_name):
            keys = valid_keys(dict_name)
            if val not in keys:
                raise ValidationError(
                    f"Invalid {dict_name[:-1]} '{val}'. Valid keys: {keys}"
                )

        check(self.genre, "genres")
        check(self.mood, "moods")
        check(self.vocal_type, "vocal_types")

        if self.energy:
            check(self.energy, "energies")
        if self.production:
            check(self.production, "productions")

        # Normalize tempo
        t = str(self.tempo).strip()
        self.tempo = t if t.upper().endswith("BPM") else f"{t} BPM"

        # Cap and validate instruments
        if len(self.instruments) > MAX_INSTRUMENTS:
            self.instruments = self.instruments[:MAX_INSTRUMENTS]
        valid_instr = valid_keys("instruments")
        for instr in self.instruments:
            if instr not in valid_instr:
                raise ValidationError(
                    f"Invalid instrument '{instr}'. Valid keys: {valid_instr}"
                )

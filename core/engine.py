"""Core prompt generation engine — deterministic, stateless."""
from __future__ import annotations
from dataclasses import dataclass, field
from core.loader import resolve_term
from core.models import PromptInput, STYLE_LIMIT


@dataclass
class PromptResult:
    prompt: str
    char_count: int
    truncated_items: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _append_if_fits(
    parts: list[str],
    candidate: str,
    current_length: int,
    limit: int,
    dropped: list[str],
) -> tuple[list[str], int]:
    """Try to append a candidate term. Returns updated parts and length."""
    separator = ", " if parts else ""
    addition = len(separator) + len(candidate)
    if current_length + addition <= limit:
        parts.append(candidate)
        return parts, current_length + addition
    else:
        dropped.append(candidate)
        return parts, current_length


def generate_prompt(inp: PromptInput) -> PromptResult:
    """
    Generate a Suno-style prompt from validated PromptInput.
    Deterministic: same inputs always produce same output.
    """
    warnings: list[str] = []
    dropped: list[str] = []
    is_instrumental = inp.vocal_type == "no_vocals"

    # --- Resolve terms ---
    genre_term = resolve_term("genres", inp.genre)
    mood_term = resolve_term("moods", inp.mood)
    tempo_term = inp.tempo  # already normalized to "X BPM"

    # --- PRIORITY 1: Base (always included) ---
    base = [genre_term, mood_term, tempo_term]
    current_length = len(", ".join(base))
    parts = list(base)

    # Sanity check: base alone must fit
    if current_length > STYLE_LIMIT:
        warnings.append("Base terms exceed 200-char limit — prompt may be truncated.")

    # --- PRIORITY 2: Vocal type ---
    if is_instrumental:
        vocal_term = "instrumental"
    else:
        vocal_term = resolve_term("vocal_types", inp.vocal_type)
    parts, current_length = _append_if_fits(
        parts, vocal_term, current_length, STYLE_LIMIT, dropped
    )

    # --- PRIORITY 3: Instruments (joined) ---
    if inp.instruments:
        instr_terms = [resolve_term("instruments", i) for i in inp.instruments]
        joined_instr = " and ".join(instr_terms)
        parts, current_length = _append_if_fits(
            parts, joined_instr, current_length, STYLE_LIMIT, dropped
        )

    # --- PRIORITY 4: Energy ---
    if inp.energy:
        energy_term = resolve_term("energies", inp.energy)
        parts, current_length = _append_if_fits(
            parts, energy_term, current_length, STYLE_LIMIT, dropped
        )

    # --- PRIORITY 5: Production ---
    if inp.production:
        prod_term = resolve_term("productions", inp.production)
        parts, current_length = _append_if_fits(
            parts, prod_term, current_length, STYLE_LIMIT, dropped
        )

    # --- PRIORITY 6: Structure hints (first to drop) ---
    if inp.structure_hints:
        parts, current_length = _append_if_fits(
            parts, inp.structure_hints, current_length, STYLE_LIMIT, dropped
        )

    final_prompt = ", ".join(parts)

    if dropped:
        warnings.append(f"Dropped due to 200-char limit: {dropped}")

    return PromptResult(
        prompt=final_prompt,
        char_count=len(final_prompt),
        truncated_items=dropped,
        warnings=warnings,
    )

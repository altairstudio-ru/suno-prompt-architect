"""Pytest test suite — 5 acceptance criteria + bonus tests."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from core.models import PromptInput, ValidationError
from core.engine import generate_prompt


def make_input(**kwargs) -> PromptInput:
    defaults = dict(genre="ambient", mood="peaceful", tempo="60", vocal_type="no_vocals")
    defaults.update(kwargs)
    return PromptInput(**defaults)


# TC1: Basic Instrumental
def test_tc1_basic_instrumental():
    inp = make_input()
    result = generate_prompt(inp)
    assert result.prompt.endswith("instrumental"), f"Got: {result.prompt}"
    assert len(result.prompt) < 100

# TC2: Full Load ≤ 200 chars
def test_tc2_full_load():
    inp = make_input(
        genre="synthwave", mood="nostalgic", tempo="100", vocal_type="male_tenor",
        instruments=["synthesizer", "drums", "bass_guitar"],
        energy="high", production="cinematic", structure_hints="verse chorus bridge",
    )
    result = generate_prompt(inp)
    assert len(result.prompt) <= 200, f"Exceeded: {len(result.prompt)} chars"

# TC3: Overload — instruments capped, no crash
def test_tc3_overload_truncation():
    inp = PromptInput(
        genre="metal", mood="aggressive", tempo="180", vocal_type="male_baritone",
        instruments=["guitar_electric", "drums", "bass_guitar", "synthesizer", "piano"],
        energy="intense", production="raw",
        structure_hints="very long structure hint that should be dropped when character limit is reached xyz",
    )
    result = generate_prompt(inp)
    assert len(result.prompt) <= 200
    assert len(inp.instruments) == 3  # capped by validator

# TC4: Invalid Genre → ValidationError
def test_tc4_invalid_genre():
    with pytest.raises(ValidationError) as exc:
        make_input(genre="Radiohead style")
    assert "genre" in str(exc.value).lower() or "invalid" in str(exc.value).lower()

# TC5: Determinism
def test_tc5_determinism():
    params = dict(
        genre="lo_fi", mood="peaceful", tempo="80", vocal_type="no_vocals",
        instruments=["vinyl_crackle", "piano"], energy="low", production="lo_fi_prod",
    )
    r1 = generate_prompt(PromptInput(**params))
    r2 = generate_prompt(PromptInput(**params))
    assert r1.prompt == r2.prompt

# Bonus: always ≤ 200
def test_prompt_never_exceeds_200():
    inp = make_input(
        genre="electronic", mood="energetic", tempo="140", vocal_type="female_soprano",
        instruments=["synthesizer", "drums", "bass_guitar"],
        energy="intense", production="layered",
        structure_hints="long intro with buildup and a very long outro with all the things",
    )
    result = generate_prompt(inp)
    assert len(result.prompt) <= 200

# Bonus: no_vocals forces instrumental even with other hints
def test_no_vocals_forces_instrumental():
    inp = make_input(vocal_type="no_vocals", instruments=["piano"])
    result = generate_prompt(inp)
    assert "instrumental" in result.prompt

# Bonus: invalid mood
def test_invalid_mood():
    with pytest.raises(ValidationError):
        make_input(mood="supercool_mood_xyz")

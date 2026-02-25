#!/usr/bin/env python3
"""Suno Prompt Architect — CLI (Click)."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Optional

import click

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).parent))

from core.models import PromptInput, ValidationError
from core.engine import generate_prompt
from core.loader import valid_keys, load_dict, load_input_file

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """🎵 Suno Prompt Architect — generate deterministic Suno AI v5 prompts."""
    pass


@cli.command("generate")
@click.option("--genre", required=True, help="Genre ID, e.g. synthwave, lo_fi, jazz")
@click.option("--mood", required=True, help="Mood ID, e.g. nostalgic, peaceful, dark")
@click.option("--tempo", required=True, help="Tempo, e.g. '80' or '80 BPM'")
@click.option("--vocal-type", "vocal_type", required=True, help="Vocal type ID, e.g. male_tenor, no_vocals")
@click.option("--instrument", "instruments", multiple=True, help="Instrument ID (repeatable, max 3). Use 'list instruments' for valid keys.")
@click.option("--energy", default=None, type=click.Choice(["low", "medium", "high", "intense", "chill", "driving"]),
              help="Energy level ID. Choices: low, medium, high, intense, chill, driving.")
@click.option("--production", default=None,
              type=click.Choice(["raw", "polished", "vintage", "modern", "lo_fi_prod", "cinematic", "minimalist", "layered"]),
              help="Production style ID. Use 'list productions' for descriptions.")
@click.option("--hint", "hints", multiple=True,
              help="Structural hint (repeatable). E.g. --hint verse --hint chorus --hint bridge")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--from-file", "from_file", type=click.Path(exists=True), default=None, help="Load params from YAML/JSON file")
def generate(genre, mood, tempo, vocal_type, instruments, energy, production, hints, fmt, from_file):
    """Generate a Suno AI v5 style prompt from musical parameters."""

    if from_file:
        # load_input_file поддерживает .yaml/.yml/.json автоматически
        data = load_input_file(from_file)
        genre = data.get("genre", genre)
        mood = data.get("mood", mood)
        tempo = str(data.get("tempo", tempo))
        vocal_type = data.get("vocal_type", vocal_type)
        instruments = data.get("instruments", list(instruments))
        energy = data.get("energy", energy)
        production = data.get("production", production)
        # hints поддерживается как list или строка
        file_hints = data.get("hints", data.get("structure_hints"))
        if file_hints:
            hints = file_hints if isinstance(file_hints, (list, tuple)) else [file_hints]

    # Объединяем повторяемые --hint в одну строку для PromptInput
    structure_hints = ", ".join(hints) if hints else None

    try:
        inp = PromptInput(
            genre=genre,
            mood=mood,
            tempo=tempo,
            vocal_type=vocal_type,
            instruments=list(instruments),
            energy=energy,
            production=production,
            structure_hints=structure_hints,
        )
    except ValidationError as e:
        click.echo(f"❌ ValidationError: {e}", err=True)
        sys.exit(1)

    result = generate_prompt(inp)

    if fmt == "json":
        click.echo(json.dumps({
            "prompt": result.prompt,
            "char_count": result.char_count,
            "truncated_items": result.truncated_items,
            "warnings": result.warnings,
        }, ensure_ascii=False, indent=2))
    else:
        click.echo(f"\n🎵 Suno Prompt ({result.char_count}/200 chars):")
        click.echo(f"   {result.prompt}\n")
        if result.warnings:
            for w in result.warnings:
                click.echo(f"⚠  {w}")


@cli.command("list")
@click.argument("dictionary", type=click.Choice(
    ["genres", "moods", "instruments", "vocal_types", "energies", "productions"]
))
def list_keys(dictionary):
    """List all valid keys for a given dictionary."""
    d = load_dict(dictionary)
    click.echo(f"\n📖 {dictionary}:")
    click.echo(f"{'Key':<25} {'English term':<30} {'Description'}")
    click.echo("-" * 80)
    for key in sorted(d.keys()):
        entry = d[key]
        desc = entry.get("description", "")
        click.echo(f"{key:<25} {entry['en']:<30} {desc}")
    click.echo()


if __name__ == "__main__":
    cli()

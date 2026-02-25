#!/usr/bin/env python3
"""Suno Prompt Architect — CLI (Click)."""
from __future__ import annotations

import json
import sys
import subprocess
import platform
from pathlib import Path
from typing import Optional

import click

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).parent))

from core.models import PromptInput, ValidationError
from core.engine import generate_prompt
from core.loader import valid_keys, load_dict, load_input_file

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Returns True on success."""
    try:
        system = platform.system()
        if system == "Darwin":
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
        elif system == "Windows":
            subprocess.run(["clip"], input=text.encode("utf-16"), check=True)
        else:  # Linux
            try:
                subprocess.run(["xclip", "-selection", "clipboard"],
                               input=text.encode(), check=True)
            except FileNotFoundError:
                subprocess.run(["xsel", "--clipboard", "--input"],
                               input=text.encode(), check=True)
        return True
    except Exception:
        return False


def _build_prompt_input(data: dict) -> PromptInput:
    """Build and validate PromptInput from a plain dict."""
    hints = data.get("hints", data.get("structure_hints"))
    if isinstance(hints, (list, tuple)):
        structure_hints = ", ".join(hints)
    elif isinstance(hints, str):
        structure_hints = hints
    else:
        structure_hints = None

    return PromptInput(
        genre=data["genre"],
        mood=data["mood"],
        tempo=str(data["tempo"]),
        vocal_type=data["vocal_type"],
        instruments=data.get("instruments", []),
        energy=data.get("energy"),
        production=data.get("production"),
        structure_hints=structure_hints,
    )


def _print_result(result, fmt: str, copy: bool, label: str = "") -> None:
    """Print a PromptResult in the requested format and optionally copy it."""
    if fmt == "json":
        click.echo(json.dumps({
            "label": label,
            "prompt": result.prompt,
            "char_count": result.char_count,
            "truncated_items": result.truncated_items,
            "warnings": result.warnings,
        }, ensure_ascii=False, indent=2))
    else:
        title = f"🎵 {label} " if label else "🎵 "
        click.echo(f"\n{title}Suno Prompt ({result.char_count}/200 chars):")
        click.echo(f"   {result.prompt}\n")
        if result.warnings:
            for w in result.warnings:
                click.echo(f"⚠  {w}")

    if copy and fmt != "json":
        ok = _copy_to_clipboard(result.prompt)
        click.echo("📋 Скопировано в буфер обмена." if ok
                   else "⚠  Не удалось скопировать: буфер обмена недоступен.")


# ─── CLI GROUP ────────────────────────────────────────────────────────────────

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """🎵 Suno Prompt Architect — generate deterministic Suno AI v5 prompts."""
    pass


# ─── COMMAND: generate ───────────────────────────────────────────────────────

@cli.command("generate")
@click.option("--genre", required=True, help="Genre ID, e.g. synthwave, lo_fi, jazz")
@click.option("--mood", required=True, help="Mood ID, e.g. nostalgic, peaceful, dark")
@click.option("--tempo", required=True, help="Tempo, e.g. '80' or '80 BPM'")
@click.option("--vocal-type", "vocal_type", required=True,
              help="Vocal type ID, e.g. male_tenor, no_vocals")
@click.option("--instrument", "instruments", multiple=True,
              help="Instrument ID (repeatable, max 3).")
@click.option("--energy", default=None,
              type=click.Choice(["low", "medium", "high", "intense", "chill", "driving"]),
              help="Energy level ID.")
@click.option("--production", default=None,
              type=click.Choice(["raw", "polished", "vintage", "modern",
                                 "lo_fi_prod", "cinematic", "minimalist", "layered"]),
              help="Production style ID.")
@click.option("--hint", "hints", multiple=True,
              help="Structural hint (repeatable). E.g. --hint verse --hint chorus")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]),
              default="text", help="Output format")
@click.option("--from-file", "from_file", type=click.Path(exists=True),
              default=None, help="Load params from YAML/JSON file")
@click.option("--copy", is_flag=True, default=False,
              help="Copy generated prompt to clipboard")
def generate(genre, mood, tempo, vocal_type, instruments, energy,
             production, hints, fmt, from_file, copy):
    """Generate a single Suno AI v5 style prompt."""

    if from_file:
        data = load_input_file(from_file)
        genre      = data.get("genre", genre)
        mood       = data.get("mood", mood)
        tempo      = str(data.get("tempo", tempo))
        vocal_type = data.get("vocal_type", vocal_type)
        instruments = data.get("instruments", list(instruments))
        energy     = data.get("energy", energy)
        production = data.get("production", production)
        file_hints = data.get("hints", data.get("structure_hints"))
        if file_hints:
            hints = file_hints if isinstance(file_hints, (list, tuple)) else [file_hints]

    structure_hints = ", ".join(hints) if hints else None

    try:
        inp = PromptInput(
            genre=genre, mood=mood, tempo=tempo, vocal_type=vocal_type,
            instruments=list(instruments), energy=energy,
            production=production, structure_hints=structure_hints,
        )
    except ValidationError as e:
        click.echo(f"❌ ValidationError: {e}", err=True)
        sys.exit(1)

    result = generate_prompt(inp)
    _print_result(result, fmt, copy)


# ─── COMMAND: album ───────────────────────────────────────────────────────────

@cli.command("album")
@click.option("--file", "album_file", required=True, type=click.Path(exists=True),
              help="Path to album JSON/YAML file (see examples/album_example.json)")
@click.option("--output", default=None,
              help="Save all prompts to a text file (e.g. album_prompts.txt)")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]),
              default="text", help="Output format")
@click.option("--copy", is_flag=True, default=False,
              help="Copy all prompts to clipboard (newline-separated)")
def album(album_file, output, fmt, copy):
    """Generate prompts for every track in an album file.

    \b
    Example:
        python cli.py album --file examples/album_example.json
        python cli.py album --file examples/album_example.json --output prompts.txt
    """
    data = load_input_file(album_file)

    if "tracks" not in data:
        click.echo("❌ Файл не содержит поле 'tracks'. "
                   "Используй examples/album_example.json как шаблон.", err=True)
        sys.exit(1)

    base = data.get("base_params", {})
    theme = data.get("theme", "Album")
    tracks = data["tracks"]

    if fmt == "text":
        click.echo(f"\n🎼 Альбом: {theme}  ({len(tracks)} треков)\n")
        click.echo("─" * 60)

    results_json = []
    all_prompts = []

    for i, track in enumerate(tracks, 1):
        # Мержим base_params + индивидуальные поля трека
        merged = {**base, **track}
        title = merged.pop("title", f"Track {i}")
        # Убираем служебные поля
        merged.pop("_comment", None)
        merged.pop("_version", None)

        try:
            inp = _build_prompt_input(merged)
        except (ValidationError, KeyError) as e:
            click.echo(f"❌ Трек {i} «{title}»: {e}", err=True)
            continue

        result = generate_prompt(inp)
        all_prompts.append(f"{title}: {result.prompt}")

        if fmt == "json":
            results_json.append({
                "track": i,
                "title": title,
                "prompt": result.prompt,
                "char_count": result.char_count,
                "truncated_items": result.truncated_items,
                "warnings": result.warnings,
            })
        else:
            click.echo(f"\n  [{i}/{len(tracks)}] {title}")
            click.echo(f"  ({result.char_count}/200) {result.prompt}")
            if result.truncated_items:
                click.echo(f"  ⚠  Обрезано: {result.truncated_items}")

    if fmt == "json":
        click.echo(json.dumps({
            "theme": theme,
            "total_tracks": len(tracks),
            "tracks": results_json,
        }, ensure_ascii=False, indent=2))
    else:
        click.echo(f"\n{'─' * 60}")
        click.echo(f"✅ Готово: {len(all_prompts)} из {len(tracks)} треков\n")

    # Сохранение в файл
    if output:
        out_path = Path(output)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"Album: {theme}\n")
            f.write("=" * 60 + "\n\n")
            for line in all_prompts:
                f.write(line + "\n")
        click.echo(f"💾 Сохранено в {out_path}")

    # Копирование в буфер
    if copy:
        text = "\n".join(all_prompts)
        ok = _copy_to_clipboard(text)
        click.echo("📋 Все промты скопированы в буфер обмена." if ok
                   else "⚠  Не удалось скопировать: буфер обмена недоступен.")


# ─── COMMAND: variation ───────────────────────────────────────────────────────

@cli.command("variation")
@click.option("--genre", required=True)
@click.option("--mood", required=True)
@click.option("--tempo", required=True)
@click.option("--vocal-type", "vocal_type", required=True)
@click.option("--instrument", "instruments", multiple=True)
@click.option("--energy", default=None,
              type=click.Choice(["low", "medium", "high", "intense", "chill", "driving"]))
@click.option("--production", default=None,
              type=click.Choice(["raw", "polished", "vintage", "modern",
                                 "lo_fi_prod", "cinematic", "minimalist", "layered"]))
@click.option("--hint", "hints", multiple=True)
@click.option("--vary", required=True,
              type=click.Choice(["mood", "energy", "vocal_type", "production", "instruments"]),
              help="Which parameter to vary across versions")
@click.option("--values", required=True,
              help="Comma-separated values for the varied parameter. "
                   "E.g. --values 'peaceful,dark,epic'")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]),
              default="text", help="Output format")
@click.option("--copy", is_flag=True, default=False,
              help="Copy all variations to clipboard")
def variation(genre, mood, tempo, vocal_type, instruments, energy,
              production, hints, vary, values, fmt, copy):
    """Generate multiple prompt variations by changing one parameter.

    \b
    Example — vary mood:
        python cli.py variation --genre synthwave --mood nostalgic --tempo 100
            --vocal-type male_tenor --vary mood --values "peaceful,dark,epic"

    \b
    Example — vary energy:
        python cli.py variation --genre lo_fi --mood peaceful --tempo 80
            --vocal-type no_vocals --vary energy --values "low,medium,high"
    """
    base_params = dict(
        genre=genre, mood=mood, tempo=tempo, vocal_type=vocal_type,
        instruments=list(instruments), energy=energy, production=production,
        structure_hints=", ".join(hints) if hints else None,
    )

    variants = [v.strip() for v in values.split(",") if v.strip()]
    if not variants:
        click.echo("❌ --values не может быть пустым", err=True)
        sys.exit(1)

    if fmt == "text":
        click.echo(f"\n🔀 Вариации по параметру «{vary}»  ({len(variants)} шт.)\n")
        click.echo("─" * 60)

    results_json = []
    all_prompts = []

    for i, val in enumerate(variants, 1):
        params = dict(base_params)

        if vary == "instruments":
            params["instruments"] = [v.strip() for v in val.split("+")]
        else:
            params[vary] = val

        label = f"{vary}={val}"

        try:
            inp = PromptInput(**params)
        except ValidationError as e:
            click.echo(f"❌ Вариант {i} ({label}): {e}", err=True)
            continue

        result = generate_prompt(inp)
        all_prompts.append(f"{label}: {result.prompt}")

        if fmt == "json":
            results_json.append({
                "variant": i,
                "label": label,
                "varied_value": val,
                "prompt": result.prompt,
                "char_count": result.char_count,
                "truncated_items": result.truncated_items,
            })
        else:
            click.echo(f"\n  Вариант {i}  [{label}]")
            click.echo(f"  ({result.char_count}/200) {result.prompt}")
            if result.truncated_items:
                click.echo(f"  ⚠  Обрезано: {result.truncated_items}")

    if fmt == "json":
        click.echo(json.dumps({
            "varied_param": vary,
            "variants": results_json,
        }, ensure_ascii=False, indent=2))
    else:
        click.echo(f"\n{'─' * 60}")
        click.echo(f"✅ Готово: {len(all_prompts)} вариаций\n")

    if copy:
        text = "\n".join(all_prompts)
        ok = _copy_to_clipboard(text)
        click.echo("📋 Все вариации скопированы в буфер обмена." if ok
                   else "⚠  Не удалось скопировать: буфер обмена недоступен.")


# ─── COMMAND: list ───────────────────────────────────────────────────────────

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

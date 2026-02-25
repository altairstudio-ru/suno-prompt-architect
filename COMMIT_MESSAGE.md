# Описание коммита для GitHub

## Заголовок (72 символа максимум)

```
feat: initial release of Suno Prompt Architect v1.0.0
```

---

## Тело коммита (полное)

```
feat: initial release of Suno Prompt Architect v1.0.0

Deterministic CLI tool for generating structured Suno AI v5 style
prompts. Same inputs always produce the same output, enabling
consistent style across albums and reproducible A/B testing.

Core features:
- Priority-based truncation algorithm (P1–P6) that always fits
  the strict 200-character Suno "Style" field limit
- External YAML dictionaries — no hardcoded strings in code
  · 67 genres  · 33 moods  · 53 instruments  · 19 vocal types
- Input validation with clear error messages (no Pydantic required)
- YAML and JSON file input via --from-file flag
- Text and JSON output modes for automation

CLI (Click):
- `generate` — create a prompt from flags or a file
  --genre, --mood, --tempo, --vocal-type  (required)
  --instrument (repeatable, max 3)
  --energy, --production  (validated choices)
  --hint (repeatable structural hints)
  --format text|json
  --from-file .yaml/.yml/.json
- `list <dictionary>` — browse all valid keys

Web API (FastAPI, optional):
- POST /generate  — REST endpoint
- GET  /health    — health check
- Swagger UI at /docs

Testing:
- 5 acceptance test cases (TC1–TC5) covering instrumental tracks,
  full parameter load, overload truncation, invalid input rejection,
  and A/B determinism
- 3 bonus tests for edge cases

Documentation:
- README.md with full usage guide (RU)
- docs/ARCHITECTURE.md — data flow, module responsibilities
- docs/DICTIONARIES.md — complete key reference tables
- CHANGELOG.md — Keep a Changelog format
- examples/album_example.json — 4-track "Cyberpunk Night" album

Fixes:
- api.py: moved `from __future__ import annotations` to first line
  (was causing SyntaxError)
- cli.py: replaced duplicate YAML/JSON parsing with loader.load_input_file()
- core/loader.py: extension check now precedes file-existence check
  so unsupported formats (.csv etc.) are rejected before stat()
```

---

## Теги и структура веток для GitHub

```bash
# Создать тег релиза
git tag -a v1.0.0 -m "Initial release: Suno Prompt Architect v1.0.0"
git push origin v1.0.0
```

Рекомендуемая структура веток:
```
main          — стабильный релиз
dev           — текущая разработка
feature/album — будущая команда album
```

---

## GitHub Topics (теги репозитория)

```
suno  ai-music  prompt-engineering  cli  python  generative-music
music-production  suno-ai  prompt-generator  deterministic
```

---

## Описание репозитория (одна строка)

```
Deterministic CLI tool for generating structured Suno AI v5 style prompts with 200-char limit handling
```

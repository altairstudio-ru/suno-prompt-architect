# Changelog

## [1.1.0] — 2025-02-25

### Добавлено

#### Команда `album`
Пакетная генерация промтов для всех треков альбома из одного JSON/YAML-файла.
`base_params` автоматически мержатся с индивидуальными параметрами каждого трека.

```bash
python3 cli.py album --file examples/album_example.json
python3 cli.py album --file examples/album_example.json --output prompts.txt
python3 cli.py album --file examples/album_example.json --format json
```

#### Команда `variation`
A/B-тестирование: генерация нескольких вариантов промта с изменением одного параметра.
Поддерживаемые параметры для вариации: `mood`, `energy`, `vocal_type`, `production`, `instruments`.

```bash
python3 cli.py variation --genre synthwave --mood nostalgic --tempo 100 \
  --vocal-type male_tenor --vary mood --values "peaceful,dark,epic"
```

#### Флаг `--copy`
Копирование готового промта (или всех промтов альбома/вариаций) в буфер обмена.
Поддерживаются Windows (`clip`), macOS (`pbcopy`), Linux (`xclip` / `xsel`).
Доступен в командах `generate`, `album`, `variation`.

```bash
python3 cli.py generate --genre lo_fi --mood peaceful --tempo 80 \
  --vocal-type no_vocals --copy
```

### Изменено
- `cli.py` рефакторинг: общая логика вынесена в хелперы `_build_prompt_input()`,
  `_print_result()`, `_copy_to_clipboard()`

---

## [1.0.0] — 2025-02-24

### Первый публичный релиз

- Детерминированный алгоритм генерации промтов (P1–P6), лимит 200 символов
- CLI (Click): команды `generate`, `list`
- Загрузка из файла: `.yaml`, `.yml`, `.json`
- Web API (FastAPI): `POST /generate`, `GET /health`
- Словари: 67 жанров, 33 настроения, 53 инструмента, 19 типов вокала
- Тесты: TC1–TC5 + 3 бонусных

---

## [Unreleased]

### Запланировано
- Флаги `--era` и `--region` для временного и регионального колорита
- Web UI (FastAPI + HTMX) — генерация в браузере без терминала
- Интеграция с Suno API

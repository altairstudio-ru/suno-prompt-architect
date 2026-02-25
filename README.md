# 🎵 Suno Prompt Architect

> Детерминированный CLI-инструмент для генерации структурированных промтов для **Suno AI v5**.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Suno Prompt Architect устраняет ручной подбор промтов методом проб и ошибок. Вы описываете трек через параметры (жанр, настроение, темп, инструменты), а инструмент собирает правильно сформатированный промт, который **всегда укладывается в лимит 200 символов** поля "Style" в Suno AI.

Одни и те же входные данные всегда дают одинаковый результат — это принципиально для A/B-тестирования и поддержки консистентного стиля альбома.

---

## Содержание

- [Возможности](#возможности)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [CLI-команды](#cli-команды)
- [Загрузка из файла](#загрузка-из-файла)
- [Web API (FastAPI)](#web-api-fastapi)
- [Словари данных](#словари-данных)
- [Алгоритм приоритетов](#алгоритм-приоритетов)
- [Тестирование](#тестирование)
- [Структура проекта](#структура-проекта)
- [Дорожная карта](#дорожная-карта)

---

## Возможности

- **Детерминированность** — одинаковые входные данные всегда дают одинаковый промт
- **200-символьный лимит** — автоматическая расстановка приоритетов и обрезка без потери смысла
- **Внешние словари** — 67 жанров, 33 настроения, 53 инструмента, 19 типов вокала в YAML-файлах
- **Два режима ввода** — флаги CLI или файл (`.yaml` / `.json`)
- **Два формата вывода** — читаемый текст или JSON для автоматизации
- **Web API** — опциональный FastAPI-сервер с автодокументацией Swagger
- **Валидация** — понятные ошибки при неверных ключах словарей

---

## Установка

```bash
git clone https://github.com/your-username/suno-prompt-architect.git
cd suno-prompt-architect

# Минимальная установка (только CLI)
pip install click pyyaml

# Полная установка (CLI + FastAPI-сервер)
pip install click pyyaml fastapi uvicorn[standard]

# Для запуска тестов
pip install pytest
```

**Требования:** Python 3.10+

---

## Быстрый старт

```bash
# Инструментальный lo-fi трек
python3 cli.py generate \
  --genre lo_fi \
  --mood peaceful \
  --tempo 80 \
  --vocal-type no_vocals \
  --instrument vinyl_crackle \
  --instrument piano

# Вывод:
# 🎵 Suno Prompt (70/200 chars):
#    lo-fi hip hop, peaceful, 80 BPM, instrumental, vinyl crackle and piano
```

```bash
# Полный synthwave трек с JSON-выводом
python3 cli.py generate \
  --genre synthwave \
  --mood nostalgic \
  --tempo 100 \
  --vocal-type male_tenor \
  --instrument synthesizer \
  --instrument drums \
  --instrument bass_guitar \
  --energy high \
  --production cinematic \
  --hint verse --hint chorus \
  --format json
```

```json
{
  "prompt": "synthwave, nostalgic, 100 BPM, male tenor vocals, synthesizer and drums and bass guitar, high energy, cinematic production, verse, chorus",
  "char_count": 140,
  "truncated_items": [],
  "warnings": []
}
```

---

## CLI-команды

### `generate` — генерация промта

```
python3 cli.py generate [OPTIONS]
```

| Флаг | Обязательный | Тип | Описание |
|------|:---:|------|---------|
| `--genre` | ✅ | string | ID жанра: `synthwave`, `lo_fi`, `post_rock`, … |
| `--mood` | ✅ | string | ID настроения: `nostalgic`, `dark`, `ethereal`, … |
| `--tempo` | ✅ | string | Темп: `80` или `80 BPM` |
| `--vocal-type` | ✅ | string | ID вокала: `male_tenor`, `no_vocals`, `ethereal_female`, … |
| `--instrument` | ❌ | string (повтор) | ID инструмента, до 3 раз |
| `--energy` | ❌ | choice | `low` / `medium` / `high` / `intense` / `chill` / `driving` |
| `--production` | ❌ | choice | `raw` / `polished` / `vintage` / `modern` / `cinematic` / … |
| `--hint` | ❌ | string (повтор) | Структурные намёки: `--hint verse --hint chorus` |
| `--format` | ❌ | choice | `text` (по умолч.) или `json` |
| `--from-file` | ❌ | path | Загрузить параметры из `.yaml` или `.json` |

### `list` — просмотр допустимых ключей

```bash
python3 cli.py list genres
python3 cli.py list moods
python3 cli.py list instruments
python3 cli.py list vocal_types
python3 cli.py list energies
python3 cli.py list productions
```

Пример вывода:

```
📖 genres:
Key                       English term                   Description
────────────────────────────────────────────────────────────────────────────────
ambient                   ambient                        Atmospheric, textural soundscapes
cinematic                 cinematic                      Epic, orchestral film-score style music
darksynth                 darksynth                      Dark, aggressive synthwave with industrial tones
...
```

---

## Загрузка из файла

Параметры можно хранить в файле и передавать через `--from-file`. Поддерживаются форматы **YAML** и **JSON**.

### Одиночный трек (YAML)

```yaml
# track.yaml
genre: post_rock
mood: haunting
tempo: 72
vocal_type: ethereal_female
instruments:
  - orchestral_strings
  - guitar_electric
  - drum_machine
energy: medium
production: cinematic
hints:
  - intro
  - verse
  - outro
```

```bash
python3 cli.py generate --from-file track.yaml
```

### Одиночный трек (JSON)

```json
{
  "genre": "darksynth",
  "mood": "melancholic",
  "tempo": 110,
  "vocal_type": "vocoder",
  "instruments": ["analog_synths", "drum_machine"],
  "energy": "chill",
  "production": "cinematic",
  "hints": ["verse", "chorus"]
}
```

```bash
python3 cli.py generate --from-file track.json
```

### Структура альбома (JSON)

Файл `examples/album_example.json` показывает будущий формат команды `album` — несколько треков с общими `base_params` и индивидуальными переопределениями:

```json
{
  "theme": "Cyberpunk Night",
  "base_params": {
    "genre": "darksynth",
    "tempo": 110,
    "vocal_type": "vocoder"
  },
  "tracks": [
    { "title": "Neon Rain",       "mood": "melancholic", "instruments": ["synth_pad", "drum_machine"] },
    { "title": "Chase Sequence",  "mood": "aggressive",  "instruments": ["synth_lead", "808_bass"], "energy": "high" }
  ]
}
```

---

## Web API (FastAPI)

```bash
# Запуск сервера
uvicorn api:app --reload

# Swagger UI
open http://localhost:8000/docs
```

### `POST /generate`

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "genre": "shoegaze",
    "mood": "dreamy",
    "tempo": "90",
    "vocal_type": "harmonized",
    "instruments": ["guitar_distorted", "synth_pad"],
    "energy": "medium"
  }'
```

```json
{
  "prompt": "shoegaze, dreamy, 90 BPM, harmonized vocals, distorted guitar and synth pad, medium energy",
  "char_count": 91,
  "truncated_items": [],
  "warnings": []
}
```

### `GET /health`

```json
{ "status": "ok" }
```

---

## Словари данных

Все строки промта берутся **только** из YAML-файлов в папке `data/`. Никаких жёстко прописанных строк в коде нет.

| Файл | Ключей | Примеры |
|------|:------:|---------|
| `genres.yaml` | 67 | `ambient`, `post_rock`, `shoegaze`, `metalcore`, `cinematic`, `bossa_nova` |
| `moods.yaml` | 33 | `melancholic`, `ethereal`, `haunting`, `bittersweet`, `cosmic`, `groovy` |
| `instruments.yaml` | 53 | `orchestral_strings`, `analog_synths`, `moog_bass`, `gated_drums`, `theremin` |
| `vocal_types.yaml` | 19 | `ethereal_female`, `gospel_choir`, `vocoder`, `harmonized`, `spoken_word` |
| `energies.yaml` | 6 | `low`, `medium`, `high`, `intense`, `chill`, `driving` |
| `productions.yaml` | 8 | `raw`, `cinematic`, `vintage`, `lo_fi_prod`, `layered` |

Чтобы добавить новый жанр, достаточно дописать запись в `data/genres.yaml`:

```yaml
my_genre:
  en: "my genre label"
  description: "Short description"
```

---

## Алгоритм приоритетов

При превышении лимита 200 символов элементы отбрасываются от низшего приоритета к высшему:

```
P1  Жанр, Настроение, Темп          → никогда не отбрасываются
P2  Тип вокала                      → критично для звука
P3  Инструменты (до 3, через "and") → высокое влияние
P4  Энергия                         → среднее влияние
P5  Стиль продакшна                 → среднее влияние
P6  Структурные намёки              → первыми отбрасываются
```

Если элемент не помещается, он попадает в поле `truncated_items` в JSON-ответе.

---

## Тестирование

```bash
# С pytest
pip install pytest
pytest tests/ -v

# Без pytest (stdlib)
python3 -m unittest discover -s tests
```

Тест-кейсы по спецификации:

| ID | Сценарий | Условие |
|----|----------|---------|
| TC1 | Инструментальный трек | Промт заканчивается на `instrumental`, длина < 100 |
| TC2 | Все поля заполнены | Длина ≤ 200 символов |
| TC3 | Перегрузка параметров | Инструменты ≤ 3, намёки отброшены, нет падения |
| TC4 | Неверный жанр | `ValidationError` с понятным сообщением |
| TC5 | A/B-консистентность | Одинаковые входные данные → одинаковый промт |

---

## Структура проекта

```
suno-prompt-architect/
│
├── cli.py                  # CLI (Click): команды generate, list
├── api.py                  # Web API (FastAPI) — опционально
├── requirements.txt        # Зависимости
├── setup.py                # Установочный скрипт
│
├── core/
│   ├── engine.py           # Алгоритм генерации + приоритетная обрезка
│   ├── loader.py           # Загрузка YAML-словарей + load_input_file (YAML/JSON)
│   └── models.py           # PromptInput: валидация, нормализация
│
├── data/
│   ├── genres.yaml         # 67 музыкальных жанров
│   ├── moods.yaml          # 33 настроения
│   ├── instruments.yaml    # 53 инструмента
│   ├── vocal_types.yaml    # 19 типов вокала
│   ├── energies.yaml       # 6 уровней энергии
│   └── productions.yaml    # 8 стилей продакшна
│
├── examples/
│   └── album_example.json  # Пример структуры альбома (4 трека)
│
└── tests/
    └── test_engine.py      # TC1–TC5 + бонусные тесты
```

---

## Дорожная карта

- [ ] Команда `album` — генерация промтов для всех треков альбома из одного JSON-файла
- [ ] Команда `ab-test` — генерация нескольких вариантов с заданными отличиями
- [ ] Флаг `--era` — временна́я привязка стиля (80s, 90s, 2000s)
- [ ] Флаг `--region` — региональный колорит (Japanese, Scandinavian, Latin)
- [ ] Интеграция с Suno API (когда появится публичный доступ)

---

## Лицензия

MIT © 2025 — свободное использование, модификация и распространение.

# Changelog

Все значимые изменения проекта документируются здесь.
Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/).

---

## [1.0.0] — 2025-02-24

### Первый публичный релиз

#### Добавлено
- **`core/engine.py`** — детерминированный алгоритм генерации промтов с приоритетной обрезкой до 200 символов
- **`core/models.py`** — `PromptInput`: валидация и нормализация входных данных без внешних зависимостей
- **`core/loader.py`** — загрузчик YAML-словарей с `lru_cache`; функция `load_input_file()` с поддержкой `.yaml`, `.yml`, `.json`
- **`cli.py`** — CLI на Click: команды `generate` и `list`
  - `--genre`, `--mood`, `--tempo`, `--vocal-type` (обязательные)
  - `--instrument` (повторяемый, максимум 3)
  - `--energy` с валидацией через `click.Choice`
  - `--production` с валидацией через `click.Choice`
  - `--hint` (повторяемый) для структурных намёков
  - `--format text|json` для выбора формата вывода
  - `--from-file` для загрузки параметров из YAML/JSON
- **`api.py`** — опциональный FastAPI-сервер: `POST /generate`, `GET /health`, Swagger UI
- **`data/genres.yaml`** — 67 жанров (электроника, рок, поп, джаз, оркестр, хип-хоп и др.)
- **`data/moods.yaml`** — 33 настроения (позитивные, меланхоличные, тёмные, атмосферные)
- **`data/instruments.yaml`** — 53 инструмента, включая `analog_synths`, `moog_bass`, `orchestral_strings`, `gated_drums`, `arpeggiator`, `808_kick`
- **`data/vocal_types.yaml`** — 19 типов вокала, включая `ethereal_female`, `gospel_choir`, `vocoder`, `harmonized`
- **`data/energies.yaml`** — 6 уровней энергии
- **`data/productions.yaml`** — 8 стилей продакшна
- **`examples/album_example.json`** — пример структуры альбома "Cyberpunk Night" (4 трека с `base_params`)
- **`tests/test_engine.py`** — 5 acceptance тестов (TC1–TC5) + 3 бонусных

#### Алгоритм приоритетов (P1–P6)
```
P1: Жанр, Настроение, Темп          — никогда не отбрасываются
P2: Тип вокала                      — критично
P3: Инструменты (до 3, через "and") — высокое влияние
P4: Энергия                         — среднее
P5: Стиль продакшна                 — среднее
P6: Структурные намёки              — первыми отбрасываются
```

---

## [Unreleased]

### Запланировано
- Команда `album` — пакетная генерация из JSON-файла альбома
- Команда `ab-test` — варианты одного трека с заданными отличиями
- Флаги `--era` и `--region` для временного и регионального колорита
- Интеграция с Suno API

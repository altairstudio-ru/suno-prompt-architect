# Архитектура Suno Prompt Architect

## Принципы дизайна

1. **Детерминированность** — никакого рандома, никаких вызовов LLM. Те же входные данные → тот же промт.
2. **Разделение ответственности** — словари, валидация, генерация и интерфейс полностью разделены.
3. **Минимум зависимостей** — ядро (`core/`) работает только на stdlib + PyYAML.
4. **Расширяемость** — новый жанр или инструмент добавляется одной строкой в YAML без правки кода.

---

## Поток данных

```
Пользователь
    │
    ▼
[CLI / API / --from-file]          ← cli.py / api.py
    │  входные параметры (dict)
    ▼
[PromptInput.__post_init__]        ← core/models.py
    │  валидация ключей через valid_keys()
    │  нормализация темпа ("80" → "80 BPM")
    │  обрезка instruments до MAX=3
    ▼
[generate_prompt(inp)]             ← core/engine.py
    │  resolve_term() для каждого поля
    │  приоритетная сборка: P1 → P2 → … → P6
    │  _append_if_fits() проверяет лимит 200 символов
    ▼
[PromptResult]
    │  .prompt      — финальная строка
    │  .char_count  — длина
    │  .truncated_items — что не вошло
    │  .warnings    — предупреждения
    ▼
Вывод: text / JSON
```

---

## Модули

### `core/loader.py`

| Функция | Описание |
|---------|---------|
| `load_dict(name)` | Загружает `data/{name}.yaml`, кэширует через `lru_cache` |
| `resolve_term(dict, key)` | Возвращает `en`-строку для ключа |
| `valid_keys(dict)` | Возвращает сортированный список ключей |
| `load_input_file(path)` | Читает `.yaml`, `.yml` или `.json`, возвращает `dict` |

Словари загружаются один раз при первом обращении и остаются в памяти весь сеанс.

### `core/models.py`

```python
@dataclass
class PromptInput:
    genre: str          # обязательный — ключ из genres.yaml
    mood: str           # обязательный — ключ из moods.yaml
    tempo: str          # обязательный — нормализуется до "X BPM"
    vocal_type: str     # обязательный — ключ из vocal_types.yaml
    energy: str | None          # опциональный
    instruments: list[str]      # опциональный, max 3
    production: str | None      # опциональный
    structure_hints: str | None # опциональный, первым отбрасывается
```

Валидация происходит в `__post_init__` — нет внешних зависимостей (Pydantic не нужен).

### `core/engine.py`

Ключевая функция `_append_if_fits()`:

```python
def _append_if_fits(parts, candidate, current_length, limit, dropped):
    addition = len(", ") + len(candidate)  # учитываем разделитель
    if current_length + addition <= limit:
        parts.append(candidate)
        return parts, current_length + addition
    else:
        dropped.append(candidate)
        return parts, current_length
```

Базовые три элемента (P1) всегда добавляются без проверки — гарантируется, что они уместятся (< 100 символов в реалистичных случаях).

---

## Форматы входных файлов

### Одиночный трек
```
genre / mood / tempo / vocal_type  — обязательные поля
instruments                        — список строк
energy / production                — строки
hints / structure_hints            — список строк или строка
```

### Структура альбома (для будущей команды `album`)
```
theme         — название альбома
base_params   — общие параметры для всех треков
tracks[]      — переопределения на трек (mood, instruments, energy, hints)
```

---

## Расширение словарей

Добавить новый жанр:

```yaml
# data/genres.yaml
my_new_genre:
  en: "my new genre"
  description: "Short description for 'list' command"
```

Добавить поля-метаданные (не влияют на промт):

```yaml
analog_synths:
  en: "analog synths"
  description: "Warm analog synthesizer tones"
  family: "electronic"      # метаданные — engine игнорирует
  priority: "high"          # метаданные — engine игнорирует
```

Только поле `en` используется в финальном промте. Все остальные поля — метаданные для команды `list`.

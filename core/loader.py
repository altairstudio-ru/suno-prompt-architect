"""Loads and caches YAML dictionaries from the data/ folder.
Also provides load_input_file() for reading YAML/JSON prompt parameter files.
"""
import json
import yaml
from pathlib import Path
from functools import lru_cache

DATA_DIR = Path(__file__).parent.parent / "data"

SUPPORTED_EXTENSIONS = {".yaml", ".yml", ".json"}


@lru_cache(maxsize=None)
def load_dict(name: str) -> dict:
    """Load a YAML dictionary by name (e.g. 'genres')."""
    path = DATA_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Dictionary file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_term(dictionary_name: str, key: str) -> str:
    """Resolve an internal key to its English string."""
    d = load_dict(dictionary_name)
    if key not in d:
        raise ValueError(f"Invalid {dictionary_name} key: '{key}'. "
                         f"Valid keys: {sorted(d.keys())}")
    return d[key]["en"]


def valid_keys(dictionary_name: str) -> list[str]:
    """Return all valid keys for a dictionary."""
    return sorted(load_dict(dictionary_name).keys())


def load_input_file(file_path) -> dict:
    """Load prompt parameters from a YAML or JSON file.

    Supported formats:
        .yaml / .yml  — YAML flat object or album structure
        .json         — JSON flat object or album structure

    Returns a plain dict.
    Raises ValueError on unsupported extension.
    Raises FileNotFoundError if path doesn't exist.
    """
    p = Path(file_path)

    ext = p.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format '{ext}'. "
            f"Supported extensions: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p}")

    with open(p, "r", encoding="utf-8") as f:
        if ext == ".json":
            data = json.load(f)
        else:
            data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(
            f"Input file must contain a JSON/YAML object (dict), "
            f"got {type(data).__name__} in '{p}'"
        )

    return data

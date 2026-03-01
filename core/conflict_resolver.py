import json
from pathlib import Path
from models.request import GenerationRequest

class ConflictResolver:
    def __init__(self):
        rules_path = Path(__file__).parent.parent / "data" / "conflict_rules.json"
        self.rules = json.loads(rules_path.read_text())

    def resolve(self, request: GenerationRequest) -> list[str]:
        warnings = []
        warnings += self._check_genre_energy(request)
        warnings += self._check_energy_mood(request)
        warnings += self._check_vocal_genre(request)
        return warnings

    def _check_genre_energy(self, request: GenerationRequest) -> list[str]:
        warnings = []
        limits = self.rules["genre_energy_limits"].get(request.genre, {})
        if "energy_max" in limits and request.energy > limits["energy_max"]:
            warnings.append(
                f"energy={request.energy} too high for {request.genre} "
                f"(max {limits['energy_max']})"
            )
        if "energy_min" in limits and request.energy < limits["energy_min"]:
            warnings.append(
                f"energy={request.energy} too low for {request.genre} "
                f"(min {limits['energy_min']})"
            )
        return warnings

    def _check_energy_mood(self, request: GenerationRequest) -> list[str]:
        warnings = []
        for rule in self.rules["energy_mood_conflicts"]["incompatible"]:
            if "energy_max" in rule and request.energy <= rule["energy_max"]:
                if request.mood in rule["forbidden_moods"]:
                    warnings.append(
                        f"mood='{request.mood}' conflicts with energy={request.energy}"
                    )
            if "energy_min" in rule and request.energy >= rule["energy_min"]:
                if request.mood in rule["forbidden_moods"]:
                    warnings.append(
                        f"mood='{request.mood}' conflicts with energy={request.energy}"
                    )
        return warnings

    def _check_vocal_genre(self, request: GenerationRequest) -> list[str]:
        warnings = []
        for rule in self.rules["vocal_genre_conflicts"]:
            if request.vocal_type == rule["vocal_type"]:
                if request.genre in rule["forbidden_genres"]:
                    warnings.append(
                        f"vocal_type='{request.vocal_type}' not recommended "
                        f"for genre='{request.genre}'"
                    )
        return warnings

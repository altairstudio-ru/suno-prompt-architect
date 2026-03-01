import json
import yaml
from pathlib import Path
from models.request import GenerationRequest
from models.response import GenerationResponse
from core.conflict_resolver import ConflictResolver
from core.style_translator import StyleTranslator
from core.hasher import generate_hash

class PromptBuilder:
    def __init__(self):
        self.resolver = ConflictResolver()
        self.translator = StyleTranslator()
        self.language_registry = self._load_json("data/language_registry.json")
        self.vocal_registry = self._load_json("data/vocal_registry.json")
        self.profiles = self._load_profiles()

    def _load_json(self, path: str) -> dict:
        return json.loads((Path(__file__).parent.parent / path).read_text())

    def _load_profiles(self) -> dict:
        profiles = {}
        profiles_dir = Path(__file__).parent.parent / "data" / "profiles"
        for f in profiles_dir.glob("*.yaml"):
            d = yaml.safe_load(f.read_text())
            profiles[d["id"]] = d
        return profiles

    def build(self, request: GenerationRequest) -> GenerationResponse:
        warnings = self.resolver.resolve(request)
        profile = self.profiles.get(request.genre, {})

        layers = []

        # Layer 0: Core
        layers.append(self._layer0(request))

        # Layer 1: Instruments
        layer1 = self._layer1(profile)
        if layer1:
            layers.append(layer1)

        # Layer 2: Vocal
        layer2 = self._layer2(request)
        if layer2:
            layers.append(layer2)

        # Layer 3: Effects
        layer3 = self._layer3(profile)
        if layer3:
            layers.append(layer3)

        # Layer 4: Style Anchor
        layer4 = self._layer4(request, profile)
        if layer4:
            layers.append(layer4)

        # Layer 5: Language fix
        layer5 = self._layer5(request)
        if layer5:
            layers.append(layer5)

        style_prompt = self._assemble(layers)

        return GenerationResponse(
            style_prompt=style_prompt,
            lyrics_meta=request.structure,
            reproducibility_hash=generate_hash(request),
            warnings=warnings,
            metadata={
                "genre": request.genre,
                "bpm": request.bpm,
                "language": request.language,
                "vocal_type": request.vocal_type,
                "char_count": len(style_prompt),
            }
        )

    def _layer0(self, request: GenerationRequest) -> str:
        return f"{request.bpm} BPM, {request.mood}"

    def _layer1(self, profile: dict) -> str:
        instruments = profile.get("instruments", [])
        return ", ".join(instruments[:3]) if instruments else ""

    def _layer2(self, request: GenerationRequest) -> str:
        if request.is_instrumental():
            return ""
        vocal = self.vocal_registry["vocal_types"].get(request.vocal_type, {})
        label = vocal.get("label", "")
        delivery = vocal.get("delivery", "")
        lang = self.language_registry["languages"].get(request.language, {})
        prefix = lang.get("vocal_prefix", "")
        parts = [p for p in [prefix, label, delivery] if p]
        return ", ".join(parts)

    def _layer3(self, profile: dict) -> str:
        effects = profile.get("effects", [])
        return ", ".join(effects[:2]) if effects else ""

    def _layer4(self, request: GenerationRequest, profile: dict) -> str:
        if request.references:
            translated = self.translator.translate_all(request.references)
            if translated:
                return translated[0]
        return profile.get("style_anchor", "")

    def _layer5(self, request: GenerationRequest) -> str:
        if request.is_instrumental():
            return "instrumental, no lyrics"
        if not request.has_lyrics():
            lang = self.language_registry["languages"].get(request.language, {})
            return lang.get("style_suffix", "")
        return ""

    def _assemble(self, layers: list[str], limit: int = 1000) -> str:
        parts = [l for l in layers if l]
        result = ", ".join(parts)
        if len(result) <= limit:
            return result
        # Обрезаем с конца пока не влезет
        while parts and len(", ".join(parts)) > limit:
            parts.pop()
        return ", ".join(parts)

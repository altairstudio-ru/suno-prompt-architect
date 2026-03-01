import json
from pathlib import Path

class StyleTranslator:
    def __init__(self):
        path = Path(__file__).parent.parent / "data" / "style_translator.json"
        self.references = json.loads(path.read_text())["references"]

    def translate(self, reference: str) -> str | None:
        return self.references.get(reference, None)

    def translate_all(self, references: list[str]) -> list[str]:
        result = []
        for ref in references:
            translated = self.translate(ref)
            if translated:
                result.append(translated)
        return result

    def available(self) -> list[str]:
        return list(self.references.keys())

import hashlib
import json
from models.request import GenerationRequest

def generate_hash(request: GenerationRequest) -> str:
    data = {
        "genre": request.genre,
        "mood": request.mood,
        "bpm": request.bpm,
        "energy": request.energy,
        "language": request.language,
        "vocal_type": request.vocal_type,
        "structure": sorted(request.structure),
        "references": sorted(request.references),
        "overrides": request.overrides,
    }
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode()).hexdigest()

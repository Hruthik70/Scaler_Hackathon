# backend/parser_groq.py
import os
import json
from groq import Groq
from models import Scene

SYSTEM_PROMPT = """
You are an animation scene generator.

Given a natural language description, you must return a single JSON object
that strictly matches this schema:

{
  "objects": [
    {
      "id": "string, unique",
      "type": "circle | rectangle | line | text",
      "x": "number (center x in pixels)",
      "y": "number (center y in pixels)",
      "color": "hex color like #FF0000",
      "radius": "number, for circle if present",
      "width": "number, for rectangle if present",
      "height": "number, for rectangle if present",
      "text": "string, only for type=text",
      "font_size": "integer, only for type=text"
    }
  ],
  "keyframes": [
    {
      "object_id": "must match an id from objects",
      "animation_type": "move | scale | rotate | fade | color_change",
      "start_time_ms": "integer >= 0",
      "duration_ms": "integer > 0",
      "from_state": "object with initial properties",
      "to_state": "object with final properties"
    }
  ],
  "total_duration_ms": "integer > 0"
}

Rules:
- Output ONLY JSON text, no explanations or markdown.
- All keyframes.object_id values must reference existing objects.id.
- Durations are in milliseconds.
- Use canvas size 1920x1080; keep shapes on screen.
"""

def parse_with_groq(description: str) -> Scene:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    client = Groq(api_key=api_key)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Return a JSON object with this top-level structure:\n"
                    "{ \"objects\": [...], \"keyframes\": [...], \"total_duration_ms\": ... }\n\n"
                    f"User description:\n{description}"
                ),
            },
        ],
        temperature=0.0,
        max_tokens=1200,
    )

    content = resp.choices[0].message.content or ""

    # Try to isolate JSON
    start = content.find("{")
    end = content.rfind("}")
    json_str = content[start:end+1]

    data = json.loads(json_str)
    if "objects" not in data and "scene" in data:
        data = data["scene"]

    return Scene(**data)

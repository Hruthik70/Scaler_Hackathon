from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# Inline models (no need for separate models.py)
class ObjectModel(BaseModel):
    id: str
    type: Literal["circle", "square", "rectangle", "text"]
    x: float = 0.0
    y: float = 0.0
    color: str = "#FFFFFF"
    radius: Optional[float] = None
    side: Optional[float] = None

class AnimationModel(BaseModel):
    object_id: str
    type: Literal["scale", "move", "fadein", "fadeout"]
    duration: float

class SceneModel(BaseModel):
    objects: List[ObjectModel]
    animations: List[AnimationModel]
    total_duration: float = 5.0

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running!"}

@app.get("/api/scene-mock")
def get_mock_scene():
    sample_scene = {
        "objects": [
            {
                "id": "circle1",
                "type": "circle",
                "x": 0,
                "y": 0,
                "color": "#FF0000",
                "radius": 1.0
            }
        ],
        "animations": [
            {
                "object_id": "circle1",
                "type": "scale",
                "duration": 3.0,
                "to_value": 3.0
            }
        ],
        "total_duration": 5.0
    }
    return sample_scene

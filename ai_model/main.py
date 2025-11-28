# ai_model/main.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class ObjectModel(BaseModel):
    id: str
    type: Literal["circle", "square", "rectangle", "text"]
    x: float = 0.0
    y: float = 0.0
    color: str = "#FFFFFF"
    radius: Optional[float] = None
    side: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    text: Optional[str] = None
    font_size: Optional[int] = 24


class AnimationModel(BaseModel):
    object_id: str
    type: Literal["scale", "move", "fadein", "fadeout"]
    duration: float = Field(gt=0)
    to_value: Optional[float] = None
    dx: Optional[float] = None
    dy: Optional[float] = None


class SceneModel(BaseModel):
    objects: List[ObjectModel]
    animations: List[AnimationModel]
    total_duration: float = Field(5.0, gt=0)


app = FastAPI()


@app.get("/")
def root():
    return {"message": "API is running!"}


@app.get("/api/scene-mock", response_model=SceneModel)
def get_mock_scene() -> SceneModel:
    return SceneModel(
        objects=[
            ObjectModel(
                id="circle1",
                type="circle",
                x=0.0,
                y=0.0,
                color="#FF0000",
                radius=1.0,
            )
        ],
        animations=[
            AnimationModel(
                object_id="circle1",
                type="scale",
                duration=3.0,
                to_value=3.0,
            )
        ],
        total_duration=5.0,
    )

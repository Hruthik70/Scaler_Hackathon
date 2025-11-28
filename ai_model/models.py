# backend/models.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any


class AnimationObject(BaseModel):
    id: str
    type: Literal["circle", "rectangle", "line", "text"]
    x: float
    y: float
    color: str = "#FFFFFF"

    # shape-specific
    radius: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None

    # text-specific
    text: Optional[str] = None
    font_size: Optional[int] = 24


class AnimationKeyframe(BaseModel):
    object_id: str
    animation_type: Literal["move", "scale", "rotate", "fade", "color_change"]
    start_time_ms: int = Field(ge=0)
    duration_ms: int = Field(gt=0)
    from_state: Dict[str, Any] = Field(default_factory=dict)
    to_state: Dict[str, Any] = Field(default_factory=dict)


class Scene(BaseModel):
    objects: List[AnimationObject]
    keyframes: List[AnimationKeyframe]
    total_duration_ms: int = Field(gt=0)
    canvas_width: int = 1920
    canvas_height: int = 1080


class AnimationRequest(BaseModel):
    description: str

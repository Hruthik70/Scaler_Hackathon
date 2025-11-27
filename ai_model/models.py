from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class ObjectModel(BaseModel):
    id: str = Field(..., description="Unique identifier for this object")
    type: Literal["circle", "square", "rectangle", "text"] = Field(..., description="Shape type")
    x: float = Field(0.0, description="X position in scene coordinates")
    y: float = Field(0.0, description="Y position in scene coordinates")
    color: str = Field("#FFFFFF", description="Hex color like #FF0000")

    # shape-specific fields
    radius: Optional[float] = Field(None, description="For circles")
    side: Optional[float] = Field(None, description="For squares")
    width: Optional[float] = Field(None, description="For rectangles")
    height: Optional[float] = Field(None, description="For rectangles")

    # text-specific
    text: Optional[str] = Field(None, description="For text objects")


class AnimationModel(BaseModel):
    object_id: str = Field(..., description="ID of target object")
    type: Literal["scale", "move", "fadein", "fadeout"] = Field(..., description="Animation type")
    duration: float = Field(..., description="Duration in seconds")

    # for scale
    from_value: Optional[float] = Field(None, description="Start scale/radius/size value")
    to_value: Optional[float] = Field(None, description="End scale/radius/size value")

    # for move
    to_x: Optional[float] = Field(None, description="Target X position")
    to_y: Optional[float] = Field(None, description="Target Y position")


class SceneModel(BaseModel):
    objects: List[ObjectModel]
    animations: List[AnimationModel]
    total_duration: float = Field(5.0, description="Extra wait at end of scene in seconds")

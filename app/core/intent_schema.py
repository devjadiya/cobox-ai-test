# app/core/intent_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ObjectIntent(BaseModel):
    type: Literal[
        "floor",
        "wall",
        "door",
        "ceiling",
        "decor",
        "track",
        "tree",
        "road",
        "building",
        "vehicle"
    ]
    count: int = Field(default=1, ge=1, le=1000)


class SceneIntent(BaseModel):
    scene_type: Literal[
        "city",
        "building",
        "track",
        "open_world",
        "custom"
    ] = "custom"

    objects: List[ObjectIntent] = []

    notes: Optional[str] = None

    # hard safety flags (future-proof)
    allow_physics: bool = False
    allow_ai_agents: bool = False
    allow_multiplayer: bool = False

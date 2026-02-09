# app/schemas/scene.py

from pydantic import BaseModel
from typing import List, Dict, Any


class IntentSchema(BaseModel):
    scene_type: str
    objects: List[Dict[str, Any]]
    notes: str | None = None
    allow_physics: bool = False
    allow_ai_agents: bool = False
    allow_multiplayer: bool = False


class AssetSchema(BaseModel):
    id: str
    category: str
    blueprint: str
    snap: bool | None = None
    foliage: bool | None = None
    meta: Dict[str, Any]


class ActorSchema(BaseModel):
    actor_id: str
    asset_id: str
    name: str
    category: str
    blueprint: str
    transform: Dict[str, Any]
    physics: Dict[str, Any]
    visibility: Dict[str, Any]


class SceneSchema(BaseModel):
    scene_id: str
    scene_type: str
    lighting: Dict[str, Any]
    fog: Dict[str, Any]
    actors: List[ActorSchema]
    rules: Dict[str, Any]


class CommandResponse(BaseModel):
    status: str
    intent: IntentSchema
    assets: List[AssetSchema]
    scene: SceneSchema

# app/core/placement_rules.py

"""
PLACEMENT RULES — ENGINE REALITY LAYER

This file encodes ALL hard constraints discovered during real engine testing.
Nothing in this file is optional.
Nothing in this file is inferred by AI.

If something breaks in the engine, it must be fixed HERE — not in prompts.
"""

from typing import Dict, List, Tuple
import itertools

# -------------------------------------------------------------------
# GLOBAL ENGINE CONSTANTS (DO NOT CHANGE)
# -------------------------------------------------------------------

DEFAULT_SCALE = {"x": 1, "y": 1, "z": 1}

DEFAULT_LIGHTING = {
    "brightness": 10.0,
    "temperature": 46.6,
    "time_of_day": 6.82,
    "sun_angle": 0.0
}

DEFAULT_FOG = {
    "density": 0.02,
    "ray_density": 0.02,
    "height": 0.2
}

GRID_SIZE = 400.0          # Unreal snap grid (observed)
FLOOR_HEIGHT = 400.0       # Height of one floor block
WALL_HEIGHT = 400.0        # Height of one wall block
DOOR_HEIGHT = 380.0        # Door opening height (safe)

MAX_ACTORS = 5000          # Hard safety cap
MAX_BUILDINGS = 20
MAX_FLOORS_PER_BUILDING = 6

# -------------------------------------------------------------------
# ASSET CATEGORY BEHAVIOR
# -------------------------------------------------------------------

ASSET_RULES = {
    "floor": {
        "snap": True,
        "allow_stack": False,      # floors CANNOT stack vertically
        "allow_physics": False,
        "collides": True
    },
    "wall": {
        "snap": True,
        "allow_stack": True,
        "allow_physics": False,
        "collides": True
    },
    "door": {
        "snap": True,
        "allow_stack": False,
        "allow_physics": False,
        "collides": False          # door ignores blockers (observed)
    },
    "ceiling": {
        "snap": True,
        "allow_stack": False,
        "allow_physics": False,
        "collides": True
    },
    "decor": {
        "snap": False,
        "allow_stack": False,
        "allow_physics": False,
        "collides": False
    },
    "foliage": {
        "snap": False,
        "allow_stack": False,
        "allow_physics": False,
        "collides": False
    },
    "track": {
        "snap": True,
        "allow_stack": False,
        "allow_physics": False,
        "collides": True
    }
}

# -------------------------------------------------------------------
# POSITION HELPERS
# -------------------------------------------------------------------

def snap_value(value: float) -> float:
    """Snap any coordinate to engine grid."""
    return round(value / GRID_SIZE) * GRID_SIZE


def make_position(x: float, y: float, z: float) -> Dict:
    """Create snapped position dict."""
    return {
        "x": snap_value(x),
        "y": snap_value(y),
        "z": snap_value(z)
    }


def default_rotation() -> Dict:
    return {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}


# -------------------------------------------------------------------
# BUILDING GENERATION LOGIC
# -------------------------------------------------------------------

def generate_building(
    building_index: int,
    base_x: float,
    base_y: float,
    floors: int,
    include_door: bool
) -> List[Dict]:
    """
    Generates a single building as a deterministic set of actors.
    """
    actors = []

    floors = min(floors, MAX_FLOORS_PER_BUILDING)
    base_z = 0.0

    # ---- FLOORS ----
    for i in range(floors):
        floor_z = base_z + (i * FLOOR_HEIGHT)

        actors.append({
            "category": "floor",
            "position": make_position(base_x, base_y, floor_z),
            "rotation": default_rotation(),
            "scale": DEFAULT_SCALE,
            "physics": False
        })

        # ---- WALLS (4 sides) ----
        wall_offsets = [
            ( GRID_SIZE, 0),
            (-GRID_SIZE, 0),
            (0,  GRID_SIZE),
            (0, -GRID_SIZE),
        ]

        for ox, oy in wall_offsets:
            actors.append({
                "category": "wall",
                "position": make_position(
                    base_x + ox,
                    base_y + oy,
                    floor_z
                ),
                "rotation": default_rotation(),
                "scale": DEFAULT_SCALE,
                "physics": False
            })

    # ---- DOOR (GROUND FLOOR ONLY) ----
    if include_door:
        actors.append({
            "category": "door",
            "position": make_position(
                base_x + GRID_SIZE,
                base_y,
                base_z
            ),
            "rotation": default_rotation(),
            "scale": DEFAULT_SCALE,
            "physics": False
        })

    # ---- CEILING ----
    actors.append({
        "category": "ceiling",
        "position": make_position(
            base_x,
            base_y,
            base_z + (floors * FLOOR_HEIGHT)
        ),
        "rotation": default_rotation(),
        "scale": DEFAULT_SCALE,
        "physics": False
    })

    return actors


# -------------------------------------------------------------------
# CITY LAYOUT LOGIC
# -------------------------------------------------------------------

def generate_city_layout(building_count: int) -> List[Tuple[float, float]]:
    """
    Generates non-overlapping building base positions.
    """
    building_count = min(building_count, MAX_BUILDINGS)

    spacing = GRID_SIZE * 4
    coords = []

    for i in range(building_count):
        x = (i % 5) * spacing
        y = (i // 5) * spacing
        coords.append((x, y))

    return coords


# -------------------------------------------------------------------
# SCENE VALIDATION
# -------------------------------------------------------------------

def validate_actor_count(actors: List[Dict]):
    if len(actors) > MAX_ACTORS:
        raise ValueError(
            f"Scene too large: {len(actors)} actors (max {MAX_ACTORS})"
        )


# -------------------------------------------------------------------
# PUBLIC ENTRYPOINT
# -------------------------------------------------------------------

def build_city_scene(intent: Dict) -> Dict:
    """
    FINAL deterministic city builder.
    Used by scene_compiler.
    """

    building_count = 0
    for obj in intent.get("objects", []):
        if obj["type"] == "building":
            building_count = obj.get("count", 1)

    city_coords = generate_city_layout(building_count)

    actors: List[Dict] = []

    for idx, (x, y) in enumerate(city_coords):
        actors.extend(
            generate_building(
                building_index=idx,
                base_x=x,
                base_y=y,
                floors=3,
                include_door=True
            )
        )

    validate_actor_count(actors)

    return {
        "lighting": DEFAULT_LIGHTING,
        "fog": DEFAULT_FOG,
        "actors": actors
    }

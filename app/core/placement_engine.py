def generate_placements(zone, asset, start_z=0):
    placements = []

    current_z = start_z

    for i in range(zone.count):
        placement = {
            "asset": asset["AssetToPlace"],
            "snap": zone.allow_snap,
            "physics": False,
            "scale": [1, 1, 1],
            "z": current_z
        }

        placements.append(placement)

        if zone.stacking:
            current_z += 1  # deterministic floor height

    return placements

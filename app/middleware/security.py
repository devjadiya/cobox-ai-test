def limit_scene(scene: dict):
    if len(scene.get("actors", [])) > 800:
        scene["actors"] = scene["actors"][:800]
    return scene

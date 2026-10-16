from __future__ import annotations

from game.map_loader import load_map


def test_authored_map_loads_collision_and_servant_mappings() -> None:
    data = load_map("assets/World/World.tmj")
    assert data.world.bounds.width == 1920
    assert data.world.bounds.height == 1088
    assert len(data.world.obstacles) == 37
    assert len(data.world.collision_polygons) == 4
    assert set(data.servant_spawns) == {1, 2, 3, 4}
    assert set(data.dropoff_zones) == {1, 2, 3, 4}
    assert len(data.pickup_zones) == 2
    assert data.world.document_source is not None


def test_authored_render_tiles_materialize_positions_and_transform_flags() -> None:
    data = load_map("assets/World/World.tmj")

    assert data.render_tiles
    assert [tile.layer_name for tile in data.render_tiles[:3]] == [
        "GroundBackground",
        "GroundBackground",
        "GroundBackground",
    ]
    transformed = [tile for tile in data.render_tiles if tile.raw_gid & 0xE0000000]
    assert transformed
    assert all(tile.tile_id == tile.raw_gid & 0x0FFFFFFF for tile in transformed)
    assert all(tile.layer_position.x >= 0 and tile.layer_position.y >= 0 for tile in transformed)


def test_authored_render_layers_preserve_transformed_tile_gids() -> None:
    data = load_map("assets/World/World.tmj")
    transformed_layers = [
        gid
        for layer in data.tile_layers
        for gid in layer.get("data", [])
        if gid & 0xE0000000
    ]
    transformed_objects = [
        obj["gid"]
        for layer in data.object_layers
        for obj in layer.get("objects", [])
        if obj.get("gid", 0) & 0xE0000000
    ]

    assert transformed_layers
    assert transformed_objects
    assert all(gid & 0x1FFFFFFF for gid in transformed_layers + transformed_objects)


def test_zero_size_polygon_objects_are_not_discarded() -> None:
    data = load_map("assets/World/World.tmj")
    assert all(len(polygon.points) >= 3 for polygon in data.world.collision_polygons)


def test_authored_interaction_properties_are_preserved() -> None:
    data = load_map("assets/World/World.tmj")
    assert len(data.pickup_properties) == 2
    assert all(properties["kind"] == "document_pickup" for properties in data.pickup_properties)
    assert all("interaction_radius" in properties for properties in data.pickup_properties)
    assert all(properties["kind"] == "document_dropoff" for properties in data.dropoff_properties.values())
    assert set(data.dropoff_properties) == {1, 2, 3, 4}
    assert data.world.fishing_pond is not None
    assert data.world.fishing_pond.stamina_regeneration


def test_map_loader_reports_missing_required_layer(tmp_path) -> None:
    import json
    from game.map_loader import MapValidationError

    source = json.loads(open("assets/World/World.tmj", encoding="utf-8").read())
    source["layers"] = [layer for layer in source["layers"] if layer.get("name") != "PlayerSpawn"]
    path = tmp_path / "missing-player-spawn.tmj"
    path.write_text(json.dumps(source), encoding="utf-8")
    try:
        load_map(path)
    except MapValidationError as exc:
        assert "PlayerSpawn" in str(exc)
    else:
        raise AssertionError("missing PlayerSpawn must fail validation")


def test_map_loader_reports_invalid_dimensions_and_malformed_polygon(tmp_path) -> None:
    import json
    from game.map_loader import MapValidationError

    source = json.loads(open("assets/World/World.tmj", encoding="utf-8").read())
    source["width"] = 59
    path = tmp_path / "invalid-dimensions.tmj"
    path.write_text(json.dumps(source), encoding="utf-8")
    try:
        load_map(path)
    except MapValidationError as exc:
        assert "60x34" in str(exc)
    else:
        raise AssertionError("invalid dimensions must fail validation")

    source["width"] = 60
    collision = next(layer for layer in source["layers"] if layer.get("name") == "Collision")
    polygon = next(obj for obj in collision["objects"] if "polygon" in obj)
    polygon["polygon"] = [{"x": 0, "y": 0}, {"x": 1, "y": 1}]
    path = tmp_path / "malformed-polygon.tmj"
    path.write_text(json.dumps(source), encoding="utf-8")
    try:
        load_map(path)
    except MapValidationError as exc:
        assert "polygon" in str(exc)
    else:
        raise AssertionError("malformed polygon must fail validation")


def test_map_loader_reports_invalid_spawn_and_servant_id_mismatch(tmp_path) -> None:
    import json
    from game.map_loader import MapValidationError

    source = json.loads(open("assets/World/World.tmj", encoding="utf-8").read())
    player_layer = next(layer for layer in source["layers"] if layer.get("name") == "PlayerSpawn")
    player_layer["objects"][0]["x"] = 2000
    path = tmp_path / "invalid-spawn.tmj"
    path.write_text(json.dumps(source), encoding="utf-8")
    try:
        load_map(path)
    except MapValidationError as exc:
        assert "PlayerSpawn" in str(exc)
    else:
        raise AssertionError("invalid spawn must fail validation")

    source = json.loads(open("assets/World/World.tmj", encoding="utf-8").read())
    drop_layer = next(layer for layer in source["layers"] if layer.get("name") == "DocumentDropOffZones")
    drop_layer["objects"][0]["properties"][-1]["value"] = 99
    path = tmp_path / "mismatched-servant-id.tmj"
    path.write_text(json.dumps(source), encoding="utf-8")
    try:
        load_map(path)
    except MapValidationError as exc:
        assert "servant_id" in str(exc)
    else:
        raise AssertionError("mismatched servant IDs must fail validation")

    source = json.loads(open("assets/World/World.tmj", encoding="utf-8").read())
    spawn_layer = next(layer for layer in source["layers"] if layer.get("name") == "CivilServantSpawnPoints")
    spawn_layer["objects"][1]["properties"][-1]["value"] = 1
    path = tmp_path / "duplicate-servant-id.tmj"
    path.write_text(json.dumps(source), encoding="utf-8")
    try:
        load_map(path)
    except MapValidationError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("duplicate servant IDs must fail validation")

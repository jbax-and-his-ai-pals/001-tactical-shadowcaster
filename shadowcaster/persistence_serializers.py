from dataclasses import asdict

from .models import Enemy, GroundItem, Item, Landmark, Quest, RectRoom, Resident, UpgradePickup
from .regions import RegionChoice


class SavedMap:
    def __init__(self, width, height, tiles, rooms, metadata=None):
        self.width: int = width
        self.height: int = height
        self.tiles: list[list[int]] = tiles
        self.rooms: list[RectRoom] = rooms
        self.metadata: dict = metadata or {}

    def is_blocked(self, x, y):
        return not (0 <= x < self.width and 0 <= y < self.height) or self.tiles[x][y] == 1


def pack_position(position):
    return None if position is None else [position[0], position[1]]


def unpack_position(position) -> tuple[int, int] | None:
    return None if position is None else (int(position[0]), int(position[1]))


def unpack_required_position(position) -> tuple[int, int]:
    return (int(position[0]), int(position[1]))


def room_to_data(room):
    return {"x": room.x, "y": room.y, "w": room.w, "h": room.h}


def room_from_data(data):
    return RectRoom(data["x"], data["y"], data["w"], data["h"])


def enemy_to_data(enemy):
    return {
        "position": pack_position(enemy.position),
        "kind": enemy.kind,
        "color": list(enemy.color),
        "damage": enemy.damage,
        "marker": enemy.marker,
        "max_health": enemy.max_health,
        "health": enemy.health,
        "on_hit_effect": enemy.on_hit_effect,
        "attack_range": enemy.attack_range,
        "preferred_range": enemy.preferred_range,
        "status_effects": enemy.status_effects,
    }


def enemy_from_data(data):
    return Enemy(
        unpack_required_position(data["position"]),
        data["kind"],
        tuple(data["color"]),
        data["damage"],
        data["marker"],
        data["max_health"],
        data["health"],
        data["on_hit_effect"],
        data.get("attack_range", 1),
        data.get("preferred_range", 1),
        data.get("status_effects", {}),
    )


def resident_to_data(resident):
    return {
        "position": pack_position(resident.position),
        "kind": resident.kind,
        "color": list(resident.color),
        "marker": resident.marker,
        "title": resident.title,
        "dialogue": list(resident.dialogue),
        "behavior": resident.behavior,
        "anchor": pack_position(resident.anchor),
        "home_name": resident.home_name,
        "name": resident.name,
        "patrol_points": [pack_position(point) for point in resident.patrol_points],
        "patrol_index": resident.patrol_index,
    }


def resident_from_data(data):
    return Resident(
        unpack_required_position(data["position"]),
        data["kind"],
        tuple(data["color"]),
        data["marker"],
        data.get("title", ""),
        tuple(data.get("dialogue", [])),
        data.get("behavior", "wander"),
        unpack_position(data.get("anchor")),
        data.get("home_name", ""),
        data.get("name", ""),
        tuple(unpack_required_position(point) for point in data.get("patrol_points", [])),
        data.get("patrol_index", 0),
    )


def pickup_to_data(pickup):
    if pickup is None:
        return None
    return {
        "position": pack_position(pickup.position),
        "kind": pickup.kind,
        "color": list(pickup.color),
        "memory_color": list(pickup.memory_color),
    }


def pickup_from_data(data):
    if data is None:
        return None
    return UpgradePickup(unpack_required_position(data["position"]), data["kind"], tuple(data["color"]), tuple(data["memory_color"]))


def landmark_to_data(landmark):
    return {
        "key": landmark.key,
        "position": pack_position(landmark.position),
        "kind": landmark.kind,
        "name": landmark.name,
        "color": list(landmark.color),
        "marker": landmark.marker,
    }


def landmark_from_data(data):
    return Landmark(
        data["key"],
        unpack_required_position(data["position"]),
        data["kind"],
        data["name"],
        tuple(data["color"]),
        data["marker"],
    )


def choice_to_data(choice):
    return asdict(choice)


def choice_from_data(data):
    return RegionChoice(**data)


def item_to_data(item):
    return asdict(item)


def item_from_data(data):
    return Item(**data)


def quest_to_data(quest):
    return {
        "id": quest.id,
        "kind": quest.kind,
        "from_world_pos": list(quest.from_world_pos),
        "to_world_pos": list(quest.to_world_pos),
        "to_town_hint": quest.to_town_hint,
        "item_key": quest.item_key,
        "item_name": quest.item_name,
        "description": quest.description,
        "reward_gold": quest.reward_gold,
        "status": quest.status,
        "target_count": quest.target_count,
        "progress_count": quest.progress_count,
        "stage": quest.stage,
        "objective_key": quest.objective_key,
        "target_region_name": quest.target_region_name,
        "target_landmark_name": quest.target_landmark_name,
        "target_landmark_kind": quest.target_landmark_kind,
        "origin_town_name": quest.origin_town_name,
    }


def quest_from_data(data):
    return Quest(
        id=data["id"],
        kind=data["kind"],
        from_world_pos=unpack_required_position(data["from_world_pos"]),
        to_world_pos=unpack_required_position(data["to_world_pos"]),
        to_town_hint=data["to_town_hint"],
        item_key=data["item_key"],
        item_name=data["item_name"],
        description=data["description"],
        reward_gold=data["reward_gold"],
        status=data.get("status", "active"),
        target_count=data.get("target_count", 0),
        progress_count=data.get("progress_count", 0),
        stage=data.get("stage", 0),
        objective_key=data.get("objective_key", ""),
        target_region_name=data.get("target_region_name", ""),
        target_landmark_name=data.get("target_landmark_name", ""),
        target_landmark_kind=data.get("target_landmark_kind", ""),
        origin_town_name=data.get("origin_town_name", ""),
    )


def ground_item_to_data(ground_item):
    return {
        "position": pack_position(ground_item.position),
        "item": item_to_data(ground_item.item),
    }


def ground_item_from_data(data):
    return GroundItem(unpack_required_position(data["position"]), item_from_data(data["item"]))


def terrain_to_data(terrain):
    return [{"position": pack_position(position), "kind": kind} for position, kind in terrain.items()]


def terrain_from_data(data):
    return {unpack_position(entry["position"]): entry["kind"] for entry in data}


def map_metadata_to_data(metadata):
    metadata = metadata or {}
    feature_footprints = metadata.get("feature_footprints", {})
    return {
        "town_buildings": metadata.get("town_buildings", []),
        "town_parent_biome": metadata.get("town_parent_biome"),
        "settlement_size": metadata.get("settlement_size"),
        "settlement_label": metadata.get("settlement_label"),
        "hostile_settlement": metadata.get("hostile_settlement", False),
        "town_square": pack_position(metadata.get("town_square")),
        "service_spot": pack_position(metadata.get("service_spot")),
        "town_paths": [pack_position(tile) for tile in sorted(metadata.get("town_paths", set()))],
        "decor": terrain_to_data(metadata.get("decor", {})),
        "feature_footprints": [
            {
                "anchor": pack_position(anchor),
                "tiles": [pack_position(tile) for tile in sorted(tiles)],
            }
            for anchor, tiles in feature_footprints.items()
        ],
        "house_colors": [{"position": pack_position(pos), "color": list(color)} for pos, color in metadata.get("house_colors", {}).items()],
        "opaque_tiles": [pack_position(tile) for tile in sorted(metadata.get("opaque_tiles", set()))],
    }


def map_metadata_from_data(data):
    data = data or {}
    return {
        "town_buildings": data.get("town_buildings", []),
        "town_parent_biome": data.get("town_parent_biome"),
        "settlement_size": data.get("settlement_size"),
        "settlement_label": data.get("settlement_label"),
        "hostile_settlement": data.get("hostile_settlement", False),
        "town_square": unpack_position(data.get("town_square")),
        "service_spot": unpack_position(data.get("service_spot")),
        "town_paths": {unpack_position(tile) for tile in data.get("town_paths", [])},
        "decor": terrain_from_data(data.get("decor", [])),
        "feature_footprints": {
            unpack_required_position(entry["anchor"]): {unpack_required_position(tile) for tile in entry.get("tiles", [])}
            for entry in data.get("feature_footprints", [])
        },
        "house_colors": {unpack_position(entry["position"]): tuple(entry["color"]) for entry in data.get("house_colors", [])},
        "opaque_tiles": {unpack_position(tile) for tile in data.get("opaque_tiles", [])},
    }


def map_to_data(map_obj):
    return {
        "width": map_obj.width,
        "height": map_obj.height,
        "tiles": map_obj.tiles,
        "rooms": [room_to_data(room) for room in map_obj.rooms],
        "metadata": map_metadata_to_data(getattr(map_obj, "metadata", {})),
    }


def map_from_data(data):
    rooms = [room_from_data(room) for room in data["rooms"]]
    return SavedMap(data["width"], data["height"], data["tiles"], rooms, map_metadata_from_data(data.get("metadata")))

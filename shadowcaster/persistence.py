import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .models import Enemy, GroundItem, Item, Landmark, Quest, RectRoom, RegionPalette, Resident, UpgradePickup
from .regions import RegionChoice, palette_for_region
from .persistence_serializers import (
    SavedMap,
    pack_position, unpack_position, unpack_required_position,
    room_to_data, room_from_data,
    enemy_to_data, enemy_from_data,
    resident_to_data, resident_from_data,
    pickup_to_data, pickup_from_data,
    landmark_to_data, landmark_from_data,
    choice_to_data, choice_from_data,
    item_to_data, item_from_data,
    quest_to_data, quest_from_data,
    ground_item_to_data, ground_item_from_data,
    terrain_to_data, terrain_from_data,
    map_metadata_to_data, map_metadata_from_data,
    map_to_data, map_from_data,
)


SAVE_DIR = Path(__file__).resolve().parents[1] / "saves"
SAVE_GLOB = "save_*.json"


def serialize_region_state(state):
    return {
        "floor": state["floor"],
        "region_type": state["region_type"],
        "region_name": state["region_name"],
        "danger_tier": state.get("danger_tier", 1),
        "danger_floor": state.get("danger_floor", state["floor"]),
        "dungeon": map_to_data(state["dungeon"]),
        "player": pack_position(state["player"]),
        "entrance": pack_position(state["entrance"]),
        "up_stairs": pack_position(state.get("up_stairs")),
        "stairs": pack_position(state["stairs"]),
        "edge_exits": [{"direction": direction, "position": pack_position(position)} for direction, position in state["edge_exits"].items()],
        "seen_tiles": [pack_position(tile) for tile in sorted(state["seen_tiles"])],
        "terrain_features": terrain_to_data(state["terrain_features"]),
        "upgrade_pickup": pickup_to_data(state["upgrade_pickup"]),
        "heal_pickup": pack_position(state["heal_pickup"]),
        "floor_items": [ground_item_to_data(ground_item) for ground_item in state.get("floor_items", [])],
        "landmarks": [landmark_to_data(landmark) for landmark in state.get("landmarks", [])],
        "enemies": [enemy_to_data(enemy) for enemy in state["enemies"]],
        "residents": [resident_to_data(resident) for resident in state["residents"]],
        "exploration_milestones": state["exploration_milestones"],
        "claimed_exploration_rewards": list(state["claimed_exploration_rewards"]),
        "claimed_surface_landmark_keys": list(state.get("claimed_surface_landmark_keys", set())),
        "region_depth": state.get("region_depth", 1),
        "region_max_depth": state.get("region_max_depth", 1),
        "player_status_sources": state.get("player_status_sources", {}),
        "service_type": state.get("service_type"),
        "service_claimed": state.get("service_claimed", False),
        "interaction_claims": list(state.get("interaction_claims", set())),
        "bottom_reward_claimed": state.get("bottom_reward_claimed", False),
        "delve_goal": pack_position(state.get("delve_goal")),
        "return_portal": pack_position(state.get("return_portal")),
        "enemies_defeated": state.get("enemies_defeated", 0),
        "enemies_spawned": state.get("enemies_spawned", len(state["enemies"])),
    }


def deserialize_region_state(data):
    return {
        "floor": data["floor"],
        "region_type": data["region_type"],
        "region_name": data["region_name"],
        "danger_tier": data.get("danger_tier", 1),
        "danger_floor": data.get("danger_floor", data["floor"]),
        "region_palette": palette_for_region(data["region_type"]),
        "dungeon": map_from_data(data["dungeon"]),
        "player": unpack_position(data.get("player")),
        "entrance": unpack_position(data["entrance"]),
        "up_stairs": unpack_position(data.get("up_stairs")),
        "stairs": unpack_position(data["stairs"]),
        "edge_exits": {entry["direction"]: unpack_position(entry["position"]) for entry in data.get("edge_exits", [])},
        "seen_tiles": {unpack_position(tile) for tile in data["seen_tiles"]},
        "terrain_features": terrain_from_data(data["terrain_features"]),
        "upgrade_pickup": pickup_from_data(data["upgrade_pickup"]),
        "heal_pickup": unpack_position(data["heal_pickup"]),
        "floor_items": [ground_item_from_data(ground_item) for ground_item in data.get("floor_items", [])],
        "landmarks": [landmark_from_data(landmark) for landmark in data.get("landmarks", [])],
        "enemies": [enemy_from_data(enemy) for enemy in data["enemies"]],
        "residents": [resident_from_data(resident) for resident in data["residents"]],
        "exploration_milestones": data["exploration_milestones"],
        "claimed_exploration_rewards": set(data["claimed_exploration_rewards"]),
        "claimed_surface_landmark_keys": set(data.get("claimed_surface_landmark_keys", [])),
        "region_depth": data.get("region_depth", 1),
        "region_max_depth": data.get("region_max_depth", 1),
        "player_status_sources": data.get("player_status_sources", {}),
        "service_type": data.get("service_type"),
        "service_claimed": data.get("service_claimed", False),
        "interaction_claims": set(data.get("interaction_claims", [])),
        "bottom_reward_claimed": data.get("bottom_reward_claimed", False),
        "delve_goal": unpack_position(data.get("delve_goal")),
        "return_portal": unpack_position(data.get("return_portal")),
        "enemies_defeated": data.get("enemies_defeated", 0),
        "enemies_spawned": data.get("enemies_spawned", len(data["enemies"])),
    }


def ensure_save_dir(path=SAVE_DIR):
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)


def next_save_path(path=SAVE_DIR):
    save_dir = ensure_save_dir(path)
    existing = sorted(save_dir.glob(SAVE_GLOB))
    numbers = []
    for file in existing:
        stem = file.stem
        suffix = stem.split("_")[-1]
        if suffix.isdigit():
            numbers.append(int(suffix))
    next_number = max(numbers, default=0) + 1
    return save_dir / f"save_{next_number:03d}.json"


def save_label(file_path):
    save_number = file_path.stem.split("_")[-1]
    stamp = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    return f"Save {save_number}  {stamp}"


def list_saves(path=SAVE_DIR):
    save_dir = Path(path)
    if not save_dir.exists():
        return []
    saves = []
    for file_path in sorted(save_dir.glob(SAVE_GLOB), reverse=True):
        saves.append({"path": file_path, "label": save_label(file_path)})
    legacy = Path(__file__).resolve().parents[1] / "savegame.json"
    if legacy.exists():
        saves.append({"path": legacy, "label": "Legacy Save"})
    return saves


def save_game(game, path=None):
    save_path = Path(path) if path else next_save_path()
    payload = {
        "world_seed": game.world_seed,
        "floor": game.floor,
        "max_health": game.max_health,
        "health": game.health,
        "weapon_name": game.weapon_name,
        "ammo": game.ammo,
        "base_light_radius": game.base_light_radius,
        "light_bonus": game.light_bonus,
        "haste_bonus": game.haste_bonus,
        "reach_bonus": game.reach_bonus,
        "melee_damage": game.melee_damage,
        "ranged_damage": game.ranged_damage,
        "gold": game.gold,
        "active_quests": [quest_to_data(q) for q in game.active_quests],
        "inventory": [item_to_data(item) for item in game.inventory],
        "player_statuses": game.player_statuses,
        "player_status_sources": game.player_status_sources,
        "facing": pack_position(game.facing),
        "region_type": game.region_type,
        "region_name": game.region_name,
        "dungeon": map_to_data(game.dungeon),
        "player": pack_position(game.player),
        "stairs": pack_position(game.stairs),
        "up_stairs": pack_position(game.up_stairs),
        "entrance": pack_position(game.entrance),
        "seen_tiles": [pack_position(tile) for tile in sorted(game.seen_tiles)],
        "travel_mode": game.travel_mode,
        "travel_choices": [choice_to_data(choice) for choice in game.travel_choices],
        "terrain_features": terrain_to_data(game.terrain_features),
        "edge_exits": [{"direction": direction, "position": pack_position(position)} for direction, position in game.edge_exits.items()],
        "world_position": pack_position(game.world_position),
        "world_regions": {key: serialize_region_state(state) for key, state in game.world_regions.items()},
        "local_regions": {key: serialize_region_state(state) for key, state in game.local_regions.items()},
        "current_local_region": game.current_local_region,
        "region_depth": game.region_depth,
        "region_max_depth": game.region_max_depth,
        "service_type": game.service_type,
        "service_claimed": game.service_claimed,
        "bottom_reward_claimed": game.bottom_reward_claimed,
        "delve_reward_pending": game.delve_reward_pending,
        "delve_goal": pack_position(game.delve_goal),
        "return_portal": pack_position(game.return_portal),
        "enemies_defeated": game.enemies_defeated,
        "enemies_spawned": game.enemies_spawned,
        "upgrade_pickup": pickup_to_data(game.upgrade_pickup),
        "heal_pickup": pack_position(game.heal_pickup),
        "floor_items": [ground_item_to_data(ground_item) for ground_item in getattr(game, "floor_items", [])],
        "landmarks": [landmark_to_data(landmark) for landmark in game.landmarks],
        "enemies": [enemy_to_data(enemy) for enemy in game.enemies],
        "residents": [resident_to_data(resident) for resident in game.residents],
        "exploration_milestones": game.exploration_milestones,
        "claimed_exploration_rewards": list(game.claimed_exploration_rewards),
        "tuning": game.tuning,
        "exploration_reward_pending": game.exploration_reward_pending,
        "completion_modal_text": game.completion_modal_text,
        "total_steps": game.total_steps,
        "total_monsters_killed": game.total_monsters_killed,
        "powerups_collected": game.powerups_collected,
        "medkits_used": game.medkits_used,
        "tonics_used": game.tonics_used,
        "best_exploration_percent": game.best_exploration_percent,
        "full_clears": game.full_clears,
        "message": game.message,
        "game_over": game.game_over,
        "death_cause": game.death_cause,
        "death_gold_lost": getattr(game, "death_gold_lost", 0),
        "death_respawn_label": getattr(game, "death_respawn_label", ""),
        "homepoint_coord": pack_position(game.homepoint_coord) if game.homepoint_coord else None,
        "discovered_shrines": [pack_position(p) for p in getattr(game, "discovered_shrines", [])],
        "player_xp": getattr(game, "player_xp", 0),
        "player_level": getattr(game, "player_level", 1),
        "xp_milestones_claimed": list(getattr(game, "xp_milestones_claimed", set())),
        "wandering_npcs": getattr(game, "wandering_npcs", {}),
        "active_ability": getattr(game, "active_ability", ""),
        "world_steps": getattr(game, "world_steps", 0),
        "trader_stock_steps": {str(k): v for k, v in getattr(game, "trader_stock_steps", {}).items()},
        "player_skills": getattr(game, "player_skills", {}),
        "player_skill_points": getattr(game, "player_skill_points", 0),
        "town_dimensions": getattr(game, "_town_dimensions", {}),
        "town_reinforcements": {k: list(v) for k, v in getattr(game, "_town_reinforcements", {}).items()},
        "town_hamlets": {k: list(v) for k, v in getattr(game, "_town_hamlets", {}).items()},
        "hamlet_security": dict(getattr(game, "_hamlet_security", {})),
        "world_notes": list(getattr(game, "_world_notes", [])),
        "road_pressure_ticks": dict(getattr(game, "_road_pressure_ticks", {})),
        "raided_towns": list(getattr(game, "_raided_towns", set())),
        "town_waystations": {k: list(v) for k, v in getattr(game, "_town_waystations", {}).items()},
    }
    save_path.write_text(json.dumps(payload), encoding="utf-8")
    return save_path


def has_save(path=SAVE_DIR):
    return len(list_saves(path)) > 0


def load_game(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data["world_seed"] = data.get("world_seed")
    data["dungeon"] = map_from_data(data["dungeon"])
    data["player"] = unpack_position(data["player"])
    data["stairs"] = unpack_position(data["stairs"])
    data["up_stairs"] = unpack_position(data.get("up_stairs"))
    data["entrance"] = unpack_position(data["entrance"])
    data["facing"] = unpack_position(data["facing"])
    data["seen_tiles"] = {unpack_position(tile) for tile in data["seen_tiles"]}
    data["terrain_features"] = terrain_from_data(data["terrain_features"])
    data["edge_exits"] = {entry["direction"]: unpack_position(entry["position"]) for entry in data.get("edge_exits", [])}
    data["world_position"] = unpack_position(data.get("world_position")) or (0, 0)
    data["current_local_region"] = data.get("current_local_region")
    data["upgrade_pickup"] = pickup_from_data(data["upgrade_pickup"])
    data["heal_pickup"] = unpack_position(data["heal_pickup"])
    data["floor_items"] = [ground_item_from_data(ground_item) for ground_item in data.get("floor_items", [])]
    data["landmarks"] = [landmark_from_data(landmark) for landmark in data.get("landmarks", [])]
    if "inventory" in data:
        data["inventory"] = [item_from_data(item) for item in data["inventory"]]
    data["gold"] = data.get("gold", 0)
    data["active_quests"] = [quest_from_data(q) for q in data.get("active_quests", [])]
    data["enemies"] = [enemy_from_data(enemy) for enemy in data["enemies"]]
    data["residents"] = [resident_from_data(resident) for resident in data["residents"]]
    data["travel_choices"] = [choice_from_data(choice) for choice in data["travel_choices"]]
    data["claimed_exploration_rewards"] = set(data["claimed_exploration_rewards"])
    data["tuning"] = data.get("tuning", {})
    data["exploration_reward_pending"] = data.get("exploration_reward_pending")
    data["completion_modal_text"] = data.get("completion_modal_text", "")
    data["delve_goal"] = unpack_position(data.get("delve_goal"))
    data["return_portal"] = unpack_position(data.get("return_portal"))
    data["total_steps"] = data.get("total_steps", 0)
    data["total_monsters_killed"] = data.get("total_monsters_killed", 0)
    data["powerups_collected"] = data.get("powerups_collected", {})
    data["medkits_used"] = data.get("medkits_used", 0)
    data["tonics_used"] = data.get("tonics_used", 0)
    data["best_exploration_percent"] = data.get("best_exploration_percent", 0)
    data["full_clears"] = data.get("full_clears", 0)
    data["region_palette"] = palette_for_region(data["region_type"])
    data["world_regions"] = {key: deserialize_region_state(state) for key, state in data.get("world_regions", {}).items()}
    data["local_regions"] = {key: deserialize_region_state(state) for key, state in data.get("local_regions", {}).items()}
    hp_raw = data.get("homepoint_coord")
    data["homepoint_coord"] = unpack_position(hp_raw) if hp_raw else None
    data["discovered_shrines"] = [unpack_position(p) for p in data.get("discovered_shrines", [])]
    data["player_xp"] = data.get("player_xp", 0)
    data["player_level"] = data.get("player_level", 1)
    data["xp_milestones_claimed"] = list(data.get("xp_milestones_claimed", []))
    data["wandering_npcs"] = data.get("wandering_npcs", {})
    data["world_steps"] = data.get("world_steps", 0)
    raw_tss = data.get("trader_stock_steps", {})
    data["trader_stock_steps"] = {
        (int(k.split(",")[0]), int(k.split(",")[1])): v for k, v in raw_tss.items()
    } if raw_tss else {}
    if not data["world_regions"]:
        data["world_regions"] = {
            "0,0": {
                "floor": data["floor"],
                "region_type": data["region_type"],
                "region_name": data["region_name"],
                "region_palette": data["region_palette"],
                "dungeon": data["dungeon"],
                "player": data["player"],
                "entrance": data["entrance"],
                "up_stairs": data.get("up_stairs"),
                "stairs": data["stairs"],
                "edge_exits": data.get("edge_exits", {}),
                "seen_tiles": data["seen_tiles"],
                "terrain_features": data["terrain_features"],
                "upgrade_pickup": data["upgrade_pickup"],
                "heal_pickup": data["heal_pickup"],
                "floor_items": data.get("floor_items", []),
                "landmarks": data.get("landmarks", []),
                "enemies": data["enemies"],
                "residents": data["residents"],
                "exploration_milestones": data["exploration_milestones"],
                "claimed_exploration_rewards": data["claimed_exploration_rewards"],
                "claimed_surface_landmark_keys": set(),
                "region_depth": data.get("region_depth", 1),
                "region_max_depth": data.get("region_max_depth", 1),
                "bottom_reward_claimed": data.get("bottom_reward_claimed", False),
                "delve_goal": data.get("delve_goal"),
                "return_portal": data.get("return_portal"),
                "enemies_defeated": data.get("enemies_defeated", 0),
                "enemies_spawned": data.get("enemies_spawned", len(data["enemies"])),
            }
        }
    return data

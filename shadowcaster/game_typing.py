from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol


if TYPE_CHECKING:
    class RegionMapLike(Protocol):
        width: int
        height: int
        tiles: list[list[int]]
        rooms: list[Any]
        metadata: dict[str, Any]
        transparent_tiles: set[tuple[int, int]]

        def is_blocked(self, x: int, y: int) -> bool: ...

    class GameMixinBase:
        # The mixins are composed into `shadowcaster.game.Game`, but Pylance
        # analyzes each mixin in isolation. Returning `Any` for unresolved
        # members suppresses false-positive attribute errors inside mixins
        # while preserving runtime behavior.
        floor_explorable_tiles: set[tuple[int, int]]
        service_modal_open: bool
        service_modal_title: str
        service_modal_lines: list[str]
        dungeon: RegionMapLike
        player: tuple[int, int]
        health: int
        max_health: int
        floor: int
        region_type: str
        region_name: str
        region_depth: int
        world_position: tuple[int, int]
        menu_mode: str | None
        world_map_open: bool
        world_map_mode: str
        selected_world_region: Any
        selected_inspect_tile: Any
        hovered_world_tile: Any
        hovered_world_region: Any
        tuning: Any
        message: Any
        stairs: Any
        up_stairs: Any
        delve_goal: Any
        return_portal: Any
        edge_exits: dict[str, tuple[int, int]]
        seen_tiles: set[tuple[int, int]]
        visible_tiles: set[tuple[int, int]]
        enemies: list[Any]
        landmarks: list[Any]
        player_statuses: Any
        danger_tier: int
        auto_move_path: list[Any]
        mouse_screen_pos: tuple[int, int]
        exploration_choice_index: int
        bottom_reward_claimed: bool
        debug_omniscient: bool
        perf_overlay: bool
        perf_timings: dict
        last_interest_tiles: Any
        upgrade_pickup: Any
        heal_pickup: Any
        def in_local_region(self) -> bool: ...
        def active_overlay(self) -> Any: ...
        def active_non_menu_overlay(self) -> Any: ...
        def has_pending_choice(self) -> bool: ...
        def stop_auto_movement(self) -> None: ...
        def __getattr__(self, name: str) -> Any: ...
else:
    class RegionMapLike:
        pass

    class GameMixinBase:
        pass

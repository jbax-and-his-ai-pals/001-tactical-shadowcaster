from __future__ import annotations

import pygame

from ..game_typing import GameMixinBase
from ..systems import can_step, find_path, heuristic


class AutoexploreMixin(GameMixinBase):

    def autoexplore_blocked_tiles(self):
        blocked = set(self.edge_exits.values())
        blocked.update(landmark.position for landmark in self.landmarks)
        blocked.update(
            tile
            for tile in (self.stairs, self.up_stairs, self.delve_goal, self.return_portal)
            if tile is not None
        )
        return blocked

    def hazardous_tile_costs(self):
        hazard_cost_by_feature = {
            "muck": 6,
            "embers": 6,
        }
        return {
            position: hazard_cost_by_feature[kind]
            for position, kind in self.terrain_features.items()
            if kind in hazard_cost_by_feature
        }

    def room_for_tile(self, tile):
        for room in getattr(self.dungeon, "rooms", []):
            if room.x <= tile[0] < room.x + room.w and room.y <= tile[1] < room.y + room.h:
                return room
        return None

    def room_unseen_tiles(self, room, blocked):
        return [
            (x, y)
            for x in range(room.x, room.x + room.w)
            for y in range(room.y, room.y + room.h)
            if (x, y) in self.floor_explorable_tiles and (x, y) not in self.seen_tiles and (x, y) not in blocked
        ]

    def frontier_tiles(self, allowed_area=None, blocked=None):
        blocked = blocked or set()
        allowed_area = allowed_area or self.floor_explorable_tiles
        frontier = []
        for tile in self.seen_tiles & self.floor_explorable_tiles:
            if tile == self.player or tile in blocked or tile not in allowed_area:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                neighbor = (tile[0] + dx, tile[1] + dy)
                if neighbor in blocked or neighbor not in allowed_area:
                    continue
                if neighbor in self.floor_explorable_tiles and neighbor not in self.seen_tiles and can_step(self.dungeon, tile, neighbor):
                    frontier.append(tile)
                    break
        return frontier

    def exploration_frontier_tiles(self):
        return self.frontier_tiles(blocked=self.autoexplore_blocked_tiles())

    def exploration_effectively_complete(self):
        if not (self.floor_explorable_tiles - self.seen_tiles):
            return True
        return not self.exploration_frontier_tiles()

    def autoexplore_interest_score(self, tile, room=None):
        score = 0
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx == 0 and dy == 0:
                    continue
                neighbor = (tile[0] + dx, tile[1] + dy)
                if neighbor in self.floor_explorable_tiles and neighbor not in self.seen_tiles:
                    score += 1
        if room is not None:
            score += max(room.w * room.h, 8)
        return score

    def best_autoexplore_target_from_tiles(self, candidates, occupied, room=None):
        best = (None, None, None)
        allowed_tiles = self.seen_tiles | set(candidates) | {self.player}
        tile_costs = self.hazardous_tile_costs()
        for target in candidates:
            path = find_path(
                self.dungeon,
                self.player,
                target,
                occupied=occupied,
                allowed_tiles=allowed_tiles,
                tile_costs=tile_costs,
            )
            if not path:
                continue
            score = self.autoexplore_interest_score(target, room=room)
            rank = (score, -len(path))
            if best[0] is None or rank > best[0]:
                best = (rank, path, target)
        return best[1], best[2]

    def find_autoexplore_path(self):
        blocked = self.autoexplore_blocked_tiles()
        occupied = {enemy.position for enemy in self.enemies if enemy.position in self.visible_tiles}
        occupied.update(resident.position for resident in self.residents if resident.position in self.visible_tiles)
        occupied.update(blocked)
        current_room = self.room_for_tile(self.player)
        if current_room:
            current_room_tiles = {
                (x, y)
                for x in range(current_room.x, current_room.x + current_room.w)
                for y in range(current_room.y, current_room.y + current_room.h)
                if (x, y) in self.floor_explorable_tiles
            }
            path, target = self.best_autoexplore_target_from_tiles(
                self.frontier_tiles(allowed_area=current_room_tiles, blocked=blocked),
                occupied,
                room=current_room,
            )
            if path:
                return path, target

        room_candidates = []
        for room in getattr(self.dungeon, "rooms", []):
            room_tiles = {
                (x, y)
                for x in range(room.x, room.x + room.w)
                for y in range(room.y, room.y + room.h)
                if (x, y) in self.floor_explorable_tiles
            }
            frontier = self.frontier_tiles(allowed_area=room_tiles, blocked=blocked)
            if frontier:
                room_candidates.append((room, frontier))
        room_candidates.sort(key=lambda item: (-len(item[1]), heuristic(self.player, item[0].center)))
        for room, frontier in room_candidates:
            path, target = self.best_autoexplore_target_from_tiles(frontier, occupied, room=room)
            if path:
                return path, target

        frontier = self.frontier_tiles(blocked=blocked)
        path, target = self.best_autoexplore_target_from_tiles(frontier, occupied)
        if path:
            return path, target
        return None, None

    def start_autoexplore(self):
        if self.run_has_ended():
            return
        if self.on_screen_hostiles():
            self.message = "Autoexplore is disabled while a hostile is in view."
            return
        if self.exploration_progress >= 100 or self.exploration_effectively_complete():
            self.exploration_progress = 100
            self.message = "This floor is already fully explored."
            return
        path, target = self.find_autoexplore_path()
        if not path or target is None:
            if self.exploration_effectively_complete():
                self.exploration_progress = 100
                self.message = "No more meaningful exploration remains on this floor."
                return
            self.message = "Autoexplore cannot find an unexplored safe route on this floor."
            self.autoexplore_active = False
            return
        self.autoexplore_active = True
        self.auto_move_path = path
        self.clear_manual_movement()
        self.next_auto_move_ms = pygame.time.get_ticks()
        self.message = f"Autoexplore heads toward tile {target[0]}, {target[1]}."

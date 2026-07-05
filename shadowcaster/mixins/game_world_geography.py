from __future__ import annotations

import random

from ..game_typing import GameMixinBase


class WorldGeographyMixin(GameMixinBase):

    def generate_world_rivers(self) -> list[list[tuple[int, int]]]:
        rivers: list[list[tuple[int, int]]] = []
        with self.seed_scope("world_rivers"):
            for _ in range(random.randint(1, 2)):
                directions = [(1, 1), (1, -1), (-1, 1), (-1, -1), (2, 1), (-2, 1), (1, 2), (-1, 2)]
                dx, dy = random.choice(directions)
                dist = random.randint(5, 9)
                cx = (dx * dist) // max(abs(dx), 1)
                cy = (dy * dist) // max(abs(dy), 1)
                path: list[tuple[int, int]] = [(cx, cy)]
                for _ in range(random.randint(5, 9)):
                    sx = -1 if cx > 0 else (1 if cx < 0 else 0)
                    sy = -1 if cy > 0 else (1 if cy < 0 else 0)
                    if random.random() < 0.3:
                        if abs(cx) >= abs(cy):
                            sy += random.choice([-1, 1])
                        else:
                            sx += random.choice([-1, 1])
                    sx = max(-1, min(1, sx))
                    sy = max(-1, min(1, sy))
                    if sx == 0 and sy == 0:
                        break
                    cx, cy = cx + sx, cy + sy
                    path.append((cx, cy))
                    if abs(cx) + abs(cy) <= 1:
                        break
                rivers.append(path)
        return rivers

    @property
    def world_river_coord_set(self) -> frozenset[tuple[int, int]]:
        coords: set[tuple[int, int]] = set()
        for path in self.world_rivers:
            coords.update(path)
        return frozenset(coords)

    _COAST_SEA_NAMES: dict[tuple[int, int], str] = {
        (0, -1): "the Northern Sea",
        (0, 1):  "the Southern Deep",
        (1, 0):  "the Eastern Sea",
        (-1, 0): "the Western Expanse",
    }

    def generate_world_coast(self) -> dict:
        with self.seed_scope("world_coast"):
            direction = random.choice([(0, -1), (0, 1), (1, 0), (-1, 0)])
            threshold = random.randint(8, 12)
        return {"direction": direction, "threshold": threshold,
                "name": self._COAST_SEA_NAMES[direction]}

    def is_ocean_coord(self, coord: tuple[int, int]) -> bool:
        if not self.world_coast:
            return False
        dx, dy = self.world_coast["direction"]
        return coord[0] * dx + coord[1] * dy > self.world_coast["threshold"]

    def coast_proximity(self, coord: tuple[int, int]) -> float:
        if not self.world_coast:
            return 0.0
        dx, dy = self.world_coast["direction"]
        proj = coord[0] * dx + coord[1] * dy
        return max(0.0, min(1.0, proj / self.world_coast["threshold"]))

    _ZONE_NAMES: dict[str, list[str]] = {
        "forest":   ["the Verdant Reaches", "the Deepwood", "the Elder Grove"],
        "swamp":    ["the Mire", "the Boglands", "the Fen"],
        "desert":   ["the Drylands", "the Dustplains", "the Wastes"],
        "mountain": ["the Heights", "the Crags", "the High Pass"],
        "tundra":   ["the Frostmark", "the Pale", "the Icefields"],
        "badlands": ["the Ashfields", "the Scorch", "the Blighted Vale"],
        "volcanic": ["the Ember Reach", "the Smoldering Rim", "the Ashen Wastes"],
        "plains":   ["the Open Country", "the Flatlands", "the Heathlands"],
        "farmland": ["the Tended Country", "the Granary", "the Fielded Vales"],
    }
    _ZONE_COLORS: dict[str, tuple[int, int, int]] = {
        "forest": (90, 160, 90), "swamp": (70, 130, 90),
        "desert": (200, 160, 80), "mountain": (150, 150, 170),
        "tundra": (160, 200, 220), "badlands": (160, 100, 60),
        "volcanic": (210, 90, 70), "plains": (160, 185, 110),
        "farmland": (145, 185, 105),
    }
    _ZONE_DIRS = [(3, 1), (-1, 3), (-3, -1), (1, -3), (2, 2), (-2, 2), (-2, -2), (2, -2)]

    def generate_world_zones(self) -> list[dict]:
        zones: list[dict] = []
        with self.seed_scope("world_zones"):
            count = random.randint(2, 3)
            dirs = random.sample(self._ZONE_DIRS, min(count, len(self._ZONE_DIRS)))
            used_names: set[str] = set()
            for i in range(count):
                dx, dy = dirs[i]
                dist = random.randint(4, 8)
                norm = max(abs(dx), abs(dy))
                cx = (dx * dist) // norm
                cy = (dy * dist) // norm
                near = dist <= 5
                if near:
                    theme = random.choice(["plains", "farmland", "forest", "swamp"])
                elif dist <= 7:
                    theme = random.choice(["forest", "mountain", "desert", "swamp", "badlands"])
                else:
                    theme = random.choice(["mountain", "tundra", "volcanic", "badlands"])
                pool = [n for n in self._ZONE_NAMES.get(theme, ["the Unknown Lands"]) if n not in used_names]
                name = random.choice(pool or self._ZONE_NAMES.get(theme, ["the Unknown Lands"]))
                used_names.add(name)
                zones.append({"center": (cx, cy), "name": name, "theme": theme,
                               "color": self._ZONE_COLORS.get(theme, (160, 160, 160))})
        return zones

    _CITY_NAMES = [
        "Ironhaven", "Duskport", "Ashford", "Greymark", "Stormgate",
        "Coldwater", "Thornwall", "Embervale", "Saltholm", "Ravenspire",
    ]
    _CITY_DISTRICT_OFFSETS: list[tuple[int, int]] = [(1, 0), (0, -1), (-1, 0)]
    _CITY_DISTRICT_TYPES = ["market", "civic", "temple"]

    def generate_world_city(self) -> dict:
        with self.seed_scope("world_city"):
            name = random.choice(self._CITY_NAMES)
            spread = [(2, 1), (-2, 1), (1, 2), (-1, 2), (2, -1), (-2, -1), (1, -2), (-1, -2)]
            dx, dy = random.choice(spread)
            hub = (dx, dy)
            districts: dict[tuple[int, int], str] = {}
            offsets = list(self._CITY_DISTRICT_OFFSETS)
            random.shuffle(offsets)
            for offset, dtype in zip(offsets, self._CITY_DISTRICT_TYPES):
                dc = (hub[0] + offset[0], hub[1] + offset[1])
                if not self.is_ocean_coord(dc) and dc != (0, 0):
                    districts[dc] = dtype
        return {"hub": hub, "name": name, "districts": districts}

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RectRoom:
    x: int
    y: int
    w: int
    h: int

    @property
    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)


@dataclass
class Enemy:
    position: tuple[int, int]
    kind: str
    color: tuple[int, int, int]
    damage: int = 1
    marker: str = "enemy"
    max_health: int = 3
    health: int = 3
    on_hit_effect: str | None = None
    attack_range: int = 1
    preferred_range: int = 1
    status_effects: dict[str, int] = field(default_factory=dict)


@dataclass
class Resident:
    position: tuple[int, int]
    kind: str
    color: tuple[int, int, int]
    marker: str = "friend"
    title: str = ""
    dialogue: tuple[str, ...] = field(default_factory=lambda: ())
    behavior: str = "wander"
    anchor: tuple[int, int] | None = None
    home_name: str = ""
    name: str = ""
    patrol_points: tuple[tuple[int, int], ...] = field(default_factory=lambda: ())
    patrol_index: int = 0


@dataclass
class UpgradePickup:
    position: tuple[int, int]
    kind: str
    color: tuple[int, int, int]
    memory_color: tuple[int, int, int]


@dataclass
class Landmark:
    key: str
    position: tuple[int, int]
    kind: str
    name: str
    color: tuple[int, int, int]
    marker: str


@dataclass
class Item:
    key: str
    name: str
    category: str
    color: tuple[int, int, int]
    marker: str
    description: str = ""
    quantity: int = 1
    melee_bonus: int = 0
    ranged_bonus: int = 0
    defense_bonus: int = 0
    heal_amount: int = 0
    cleanses: bool = False
    ward_duration: int = 0
    equipped: bool = False


@dataclass
class GroundItem:
    position: tuple[int, int]
    item: Item


@dataclass
class Quest:
    id: str
    kind: str
    from_world_pos: tuple[int, int]
    to_world_pos: tuple[int, int]
    to_town_hint: str
    item_key: str
    item_name: str
    description: str
    reward_gold: int
    status: str = "available"
    target_count: int = 0
    progress_count: int = 0
    stage: int = 0
    objective_key: str = ""
    target_region_name: str = ""
    target_landmark_name: str = ""
    target_landmark_kind: str = ""
    origin_town_name: str = ""


@dataclass(frozen=True)
class RegionPalette:
    wall: tuple[int, int, int]
    floor: tuple[int, int, int]
    memory_wall: tuple[int, int, int]
    memory_floor: tuple[int, int, int]
    banner_fill: tuple[int, int, int]
    banner_border: tuple[int, int, int]
    banner_text: tuple[int, int, int]

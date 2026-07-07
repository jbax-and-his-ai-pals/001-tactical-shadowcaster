from __future__ import annotations

import random

from ..constants import COLOR_FRIEND
from ..game_typing import GameMixinBase
from ..models import Resident


_GROWTH_RESIDENT_TIER1 = (
    "vendor", COLOR_FRIEND, "settler", "Street Vendor",
    (
        "The square's been picking up since you started coming through.",
        "Word travels — a friendly face opens a few extra doors.",
        "New stall opened last week. Your work here's noticed.",
    ),
    "plaza",
)

_GROWTH_RESIDENT_TIER2 = (
    "elder", COLOR_FRIEND, "settler", "Town Elder",
    (
        "This town's seen better years, but your help has made a real difference.",
        "The notice board's been busy since you've been through.",
        "A settlement earns its name through its decisions. So does a traveler.",
    ),
    "stationary",
)


_ARCHETYPE_THRESHOLD = 3

_ARCHETYPE_LABELS = {
    "frontier_post": "Frontier Post",
    "trade_hub": "Trade Hub",
    "learning_seat": "Learning Seat",
    "social_anchor": "Social Anchor",
    "survivor": "Survivor Settlement",
}


class TownReactionsMixin(GameMixinBase):

    # ── Town dimensions ────────────────────────────────────────────────────

    def _town_dim_key(self, coord):
        c = coord or self.world_position
        return f"{c[0]},{c[1]}"

    def town_dimensions(self, coord=None):
        key = self._town_dim_key(coord)
        dims = getattr(self, "_town_dimensions", {})
        return dims.get(key, {"security": 0, "prosperity": 0, "knowledge": 0, "connections": 0})

    def increment_town_dimension(self, dim, coord=None, amount=1):
        key = self._town_dim_key(coord)
        if not hasattr(self, "_town_dimensions"):
            self._town_dimensions = {}
        entry = self._town_dimensions.setdefault(key, {"security": 0, "prosperity": 0, "knowledge": 0, "connections": 0})
        entry[dim] = entry.get(dim, 0) + amount

    def town_archetype(self, coord=None):
        dims = self.town_dimensions(coord)
        dominant_dim = max(dims, key=lambda k: dims[k])
        dominant_val = dims[dominant_dim]
        if dominant_val < _ARCHETYPE_THRESHOLD:
            return "survivor"
        return {
            "security": "frontier_post",
            "prosperity": "trade_hub",
            "knowledge": "learning_seat",
            "connections": "social_anchor",
        }[dominant_dim]

    def town_archetype_label(self, coord=None):
        return _ARCHETYPE_LABELS.get(self.town_archetype(coord), "Settlement")

    # ── Existing attitude system ───────────────────────────────────────────

    def town_attitude_score(self, coord=None):
        coord = coord or self.world_position
        return self.town_prosperity_score(coord)

    def town_attitude_label(self, coord=None):
        score = self.town_attitude_score(coord)
        if score >= 10:
            return "Beloved"
        if score >= 6:
            return "Trusted"
        if score >= 3:
            return "Welcome"
        if score >= 1:
            return "Known"
        return "Wary"

    def town_attitude_board_summary(self, coord=None):
        label = self.town_attitude_label(coord)
        return f"Standing here: {label}."

    def town_service_bonus_tier(self, coord=None):
        score = self.town_attitude_score(coord)
        if score >= 10:
            return 2
        if score >= 6:
            return 1
        return 0

    def with_town_attitude_dialogue(self, text, resident=None):
        if self.region_type != "town" or not text:
            return text
        label = self.town_attitude_label()
        role = getattr(resident, "kind", "")
        if label == "Beloved":
            suffix = {
                "guide": "The guide treats you like one of their own now.",
                "scout": "The scout speaks to you like a trusted runner.",
                "vendor": "The vendor grins like you're good business and good company.",
            }.get(role, "People here are plainly glad to see you.")
        elif label == "Trusted":
            suffix = "You get the sense this town trusts your judgment."
        elif label == "Welcome":
            suffix = "The town seems comfortable having you around."
        elif label == "Known":
            suffix = "At least the locals recognize you now."
        else:
            suffix = "You still feel a little unproven here."
        # Level 3+: NPCs address the player by title
        if getattr(self, "player_level", 1) >= 3 and label in ("Known", "Welcome", "Trusted", "Beloved"):
            title = self.player_title() if hasattr(self, "player_title") else ""
            if title:
                text = f"{title}. {text}"
        return f"{text} {suffix}".strip()

    def town_response_line(self, coord=None):
        coord = coord or self.world_position
        score = self.town_attitude_score(coord)
        if score >= 10:
            return "The town feels genuinely lively now."
        if score >= 6:
            return "The streets feel busier than they used to."
        if score >= 3:
            return "People seem a little more at ease here."
        if score >= 1:
            return "The town is starting to recover its confidence."
        return ""

    def town_work_summary_line(self, coord=None):
        coord = coord or self.world_position
        counts = self.completed_quest_counts(coord)
        if sum(counts.values()) <= 0:
            return ""
        parts = []
        if counts.get("delivery", 0):
            parts.append(f"{counts['delivery']} deliveries")
        if counts.get("scout", 0):
            parts.append(f"{counts['scout']} reports")
        if counts.get("bounty", 0):
            parts.append(f"{counts['bounty']} bounties")
        if counts.get("chain", 0):
            parts.append(f"{counts['chain']} leads")
        return "Completed here: " + ", ".join(parts[:3]) + "."

    def resident_town_response_line(self, resident):
        if self.region_type != "town":
            return ""
        # Road pressure takes priority when roads are contested
        if hasattr(self, "road_pressure_npc_line"):
            pressure = self.road_pressure_npc_line()
            if pressure:
                return pressure
        # Wildlife pressure: surface when roads are safe but biome conditions are active
        if resident.kind in ("elder", "guide", "scout", "watch", "farmer"):
            if hasattr(self, "wildlife_pressure_npc_line"):
                wildlife = self.wildlife_pressure_npc_line()
                if wildlife:
                    return wildlife
        # Buffer zone: watch and scout residents surface patrol perimeter status
        if resident.kind in ("watch", "scout"):
            if hasattr(self, "buffer_zone_npc_line"):
                bz = self.buffer_zone_npc_line()
                if bz:
                    return bz
        # Established towns: surface archetype history or expansion state via elder/guide dialogue
        if resident.kind in ("elder", "guide"):
            expansion_line = self.town_expansion_npc_line()
            if expansion_line:
                return expansion_line
        if resident.kind in ("elder", "guide", "scout"):
            history = self.town_history_npc_line()
            if history:
                return history
        response = self.town_response_line()
        if not response:
            return ""
        role_lines = {
            "guide": "More folk are asking about the roads lately.",
            "scout": "People are taking the nearby routes more seriously now.",
            "farmer": "A steadier town means fuller tables.",
            "watch": "It's easier to hold the square when the town has heart.",
            "vendor": "Trade picks up when people feel safer.",
            "elder": "These streets remember who helps them.",
        }
        return role_lines.get(resident.kind, response)

    def town_service_preview_lines(self, coord=None):
        """Return 3-4 concrete lines showing what attitude tier means for services."""
        coord = coord or self.world_position
        tier = self.town_service_bonus_tier(coord)
        label = self.town_attitude_label(coord)
        lines = []

        # Inn preview
        inn_hp = 3 + tier
        tier1_hp = 4
        tier2_hp = 5
        inn_note = f"Inn: heals {inn_hp} HP"
        if tier == 0:
            inn_note += f" · Trusted → {tier1_hp} HP · Beloved → {tier2_hp} HP"
        elif tier == 1:
            inn_note += f" · Beloved → {tier2_hp} HP"
        lines.append(inn_note)

        # Provisioner/supply preview
        supply_ammo = 1 + tier
        supply_medkits = 1 + (1 if tier >= 2 else 0)
        sup_note = f"Provisioner: {supply_ammo} ammo, {supply_medkits} medkit{'s' if supply_medkits > 1 else ''}"
        if tier == 0:
            sup_note += " · Trusted → 2 ammo · Beloved → 2 ammo, 2 medkits"
        elif tier == 1:
            sup_note += " · Beloved → 2 ammo, 2 medkits"
        lines.append(sup_note)

        # Board preview
        slots = self.town_quest_slots(coord)
        reward_bonus = self.town_quest_reward_bonus(coord)
        board_note = f"Board: {slots} quests"
        if reward_bonus:
            board_note += f", +{reward_bonus}g each"
        score = self.town_attitude_score(coord)
        if score >= 6:
            board_note += ", priority contracts available"
        elif score >= 1:
            board_note += ", chain leads available"
        lines.append(board_note)

        if tier > 0:
            lines.append(f"Service tier {tier} active ({label} standing).")
        else:
            lines.append("Complete local contracts to unlock better services.")
        return lines

    # ── Archetype self-reinforcement ───────────────────────────────────────

    _REINFORCEMENT_NPCS = {
        "frontier_post": ("scout", "Patrol Scout", (
            "The perimeter runs east and west — I check both before nightfall.",
            "We've had fewer incidents since the patrols started.",
            "If you're heading toward the border, I can tell you what we've seen.",
        ), "wander", 5),
        "trade_hub": ("vendor", "Traveling Merchant", (
            "I set up here permanently once the caravans started coming through.",
            "Best crossroads I've found in the region. Good for business.",
            "I carry things you won't find in the standard supply. Ask.",
        ), "stationary", 5),
        "learning_seat": ("librarian", "Town Archivist", (
            "We've been collecting records from every traveler who passes through.",
            "The archive isn't large yet, but it grows with every report that comes back.",
            "If you've seen something unusual out there, I'd like to hear it.",
        ), "stationary", 5),
        "social_anchor": ("herald", "Town Diplomat", (
            "We maintain correspondence with six settlements now. Three of them responded.",
            "A town that knows its neighbors makes better decisions for itself.",
            "You've been to more towns than most. That knowledge has value here.",
        ), "wander", 5),
    }

    def _reinforcement_log(self) -> dict:
        if not hasattr(self, "_town_reinforcements"):
            self._town_reinforcements: dict = {}
        return self._town_reinforcements

    def _reinforcement_fired(self, coord_key: str, key: str) -> bool:
        return key in self._reinforcement_log().get(coord_key, set())

    def _fire_reinforcement(self, coord_key: str, key: str) -> None:
        log = self._reinforcement_log()
        log.setdefault(coord_key, set()).add(key)

    def town_reinforcement_tick(self) -> None:
        archetype = self.town_archetype()
        if archetype == "survivor":
            return
        dims = self.town_dimensions()
        coord_key = self._town_dim_key(None)
        spec = self._REINFORCEMENT_NPCS.get(archetype)
        if spec is None:
            return
        kind, title, dialogue, behavior, min_score = spec
        dominant_dim = {"frontier_post": "security", "trade_hub": "prosperity",
                        "learning_seat": "knowledge", "social_anchor": "connections"}[archetype]
        if dims.get(dominant_dim, 0) < min_score:
            return
        rkey = f"npc_{archetype}"
        if self._reinforcement_fired(coord_key, rkey):
            return
        if any(r.kind == kind and getattr(r, "is_growth_resident", False) and r.title == title
               for r in self.residents):
            self._fire_reinforcement(coord_key, rkey)
            return
        pos = self._growth_resident_tile()
        r = Resident(pos, kind, COLOR_FRIEND, "settler", title, tuple(dialogue),
                     behavior, is_growth_resident=True)
        self.residents.append(r)
        self._fire_reinforcement(coord_key, rkey)
        archetype_label = self.town_archetype_label()
        self.message = (self.message + f" {title} has established a presence here — {self.region_name} is becoming a {archetype_label}.").strip()
        if hasattr(self, "add_world_note"):
            self.add_world_note(f"{self.region_name} is developing into a {archetype_label}.", coord=self.world_position, kind="archetype")

    def load_region_state(self, state, arrival_direction=None):
        super().load_region_state(state, arrival_direction=arrival_direction)  # type: ignore[misc]
        if state.get("region_type") == "town" and arrival_direction is not None:
            self._check_town_growth()
            self.town_reinforcement_tick()
            if hasattr(self, "seed_hamlet_if_eligible"):
                self.seed_hamlet_if_eligible()
            if hasattr(self, "hamlet_fragility_tick"):
                self.hamlet_fragility_tick()
            if hasattr(self, "road_pressure_tick"):
                self.road_pressure_tick()
            if hasattr(self, "seed_waystations"):
                self.seed_waystations()
            if hasattr(self, "sell_harvest_goods"):
                sell_msg = self.sell_harvest_goods()
                if sell_msg:
                    if self.message:
                        self.message = f"{self.message} {sell_msg}"
                    else:
                        self.message = sell_msg

    def _check_town_growth(self):
        tier = self.town_service_bonus_tier()
        if tier <= self._growth_tier_acked:
            return
        self._apply_town_growth(tier)
        self._growth_tier_acked = tier
        self.store_current_region()

    def _growth_resident_tile(self):
        occupied = {r.position for r in self.residents}
        candidates = [
            tile for tile in self.floor_explorable_tiles
            if tile not in occupied and not self.dungeon.is_blocked(*tile)
        ]
        if not candidates:
            return self.entrance
        path_tiles = set(getattr(self.dungeon, "metadata", {}).get("town_paths", set()))
        path_candidates = [t for t in candidates if t in path_tiles]
        pool = path_candidates or candidates
        return random.choice(pool)

    def _apply_town_growth(self, tier):
        new_residents = []
        if tier >= 1 and not any(r.is_growth_resident for r in self.residents):
            kind, color, marker, title, dialogue, behavior = _GROWTH_RESIDENT_TIER1
            pos = self._growth_resident_tile()
            r = Resident(pos, kind, color, marker, title, dialogue, behavior, is_growth_resident=True)
            new_residents.append(r)
        if tier >= 2 and sum(1 for r in self.residents if r.is_growth_resident) < 2:
            kind, color, marker, title, dialogue, behavior = _GROWTH_RESIDENT_TIER2
            pos = self._growth_resident_tile()
            r = Resident(pos, kind, color, marker, title, dialogue, behavior, is_growth_resident=True)
            new_residents.append(r)
        self.residents.extend(new_residents)
        if new_residents:
            label = self.town_attitude_label()
            self.message = (
                f"You enter {self.region_name}. "
                f"The town feels different — standing here: {label}. "
                f"{'A new face has appeared in the square.' if len(new_residents) == 1 else 'New faces have appeared in the square.'}"
            )

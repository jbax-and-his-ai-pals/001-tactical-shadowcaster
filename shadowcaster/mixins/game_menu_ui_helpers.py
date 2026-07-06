from __future__ import annotations

import pygame

from ..constants import SCREEN_WIDTH
from ..game_typing import GameMixinBase
from ..item_generation import QUALITY_COLORS
from ..loot_catalog import GEMS, CURIOS
from ..persistence import has_save


class MenuUIHelpersMixin(GameMixinBase):

    def tuner_entries(self):
        entries = []
        for entry in self.tuner_schema():
            value = self.tuning[entry["key"]]
            display = "Yes" if entry["key"] == "heal_pickup_require_missing_hp" and value else "No" if entry["key"] == "heal_pickup_require_missing_hp" else str(value)
            entries.append({**entry, "value": value, "display": display})
        return entries

    def tuner_tabs(self):
        return ["Recovery", "Rewards", "Upgrades"]

    def grouped_tuner_entries(self):
        groups = {
            "Recovery": {"heal_pickup_floor_interval", "heal_pickup_restore", "heal_pickup_require_missing_hp", "medkit_heal"},
            "Rewards": {
                "full_explore_vitality_bonus",
                "full_explore_power_bonus",
                "full_explore_recovery_medkits",
                "full_explore_recovery_tonics",
                "bottom_reward_ammo",
                "bottom_reward_medkits",
            },
            "Upgrades": {"vitality_upgrade_amount", "power_upgrade_amount", "light_upgrade_amount"},
        }
        group_name = self.tuner_tabs()[self.tuner_tab]
        allowed = groups[group_name]
        return [entry for entry in self.tuner_entries() if entry["key"] in allowed]

    def shift_tuner_tab(self, delta):
        tabs = self.tuner_tabs()
        self.tuner_tab = (self.tuner_tab + delta) % len(tabs)
        self.tuner_index = 0
        self.message = f"Tuner tab: {tabs[self.tuner_tab]}."

    def adjust_tuner_value(self, delta):
        entries = self.grouped_tuner_entries()
        if not entries:
            return
        entry = entries[self.tuner_index]
        current = self.tuning[entry["key"]]
        new_value = max(entry["min"], min(entry["max"], current + entry["step"] * delta))
        if new_value == current:
            return
        self.tuning[entry["key"]] = new_value
        new_display = "Yes" if entry["key"] == "heal_pickup_require_missing_hp" and new_value else "No" if entry["key"] == "heal_pickup_require_missing_hp" else str(new_value)
        self.message = f"{entry['label']}: {new_display}"

    def inventory_rows(self):
        rows = []
        for item in self.inventory:
            if item.category == "consumable":
                if item.quantity <= 0:
                    continue
                rarity = getattr(item, "rarity", "common")
                rarity_tag = f"[{rarity}] " if rarity != "common" else ""
                rows.append({"key": item.key, "label": f"{item.name} ×{item.quantity}", "detail": f"{rarity_tag}{item.description or 'Use this item'}", "action": "use", "color": item.color})
            elif item.category == "weapon":
                status = "Equipped" if item.equipped else "Owned"
                parts = []
                if item.melee_bonus:
                    parts.append(f"+{item.melee_bonus} melee")
                if item.ranged_bonus:
                    parts.append(f"+{item.ranged_bonus} ranged")
                if item.max_hp_bonus:
                    parts.append(f"+{item.max_hp_bonus} HP")
                stat = ", ".join(parts) or "No stat bonus"
                quality = getattr(item, "quality", "normal")
                shows_quality = hasattr(self, "skill_shows_quality") and self.skill_shows_quality()
                shows_affixes = hasattr(self, "skill_shows_affixes") and self.skill_shows_affixes()
                if shows_affixes and (getattr(item, "prefix_key", None) or getattr(item, "suffix_key", None)):
                    affix_parts = [k for k in (item.prefix_key, item.suffix_key) if k]
                    stat = f"[{', '.join(affix_parts)}] {stat}"
                elif shows_quality and quality != "normal":
                    stat = f"[{quality}] {stat}"
                color = QUALITY_COLORS.get(quality, item.color)
                rows.append({"key": item.key, "label": f"{item.name} ({status})", "detail": stat, "action": "equip", "color": color})
            elif item.category == "armor":
                status = "Equipped" if item.equipped else "Owned"
                parts = [f"+{item.defense_bonus} def"]
                if getattr(item, "ranged_penalty", 0):
                    parts.append(f"{item.ranged_penalty} ranged")
                if getattr(item, "fov_penalty", 0):
                    parts.append(f"{item.fov_penalty} FOV")
                if getattr(item, "max_hp_bonus", 0):
                    parts.append(f"+{item.max_hp_bonus} HP")
                stat = ", ".join(parts)
                quality = getattr(item, "quality", "normal")
                shows_quality = hasattr(self, "skill_shows_quality") and self.skill_shows_quality()
                shows_affixes = hasattr(self, "skill_shows_affixes") and self.skill_shows_affixes()
                if shows_affixes and (getattr(item, "prefix_key", None) or getattr(item, "suffix_key", None)):
                    affix_parts = [k for k in (item.prefix_key, item.suffix_key) if k]
                    stat = f"[{', '.join(affix_parts)}] {stat}"
                elif shows_quality and quality != "normal":
                    stat = f"[{quality}] {stat}"
                color = QUALITY_COLORS.get(quality, item.color)
                rows.append({"key": item.key, "label": f"{item.name} ({status})", "detail": stat, "action": "equip", "color": color})
            elif item.category == "trinket":
                status = "Equipped" if item.equipped else "Owned"
                rarity = getattr(item, "rarity", "uncommon")
                rarity_tag = f"[{rarity}] " if rarity != "uncommon" else ""
                rows.append({"key": item.key, "label": f"{item.name} ({status})", "detail": f"{rarity_tag}{item.description}", "action": "equip", "color": item.color, "locked": False})
            elif item.category == "harvest":
                qty = getattr(item, "quantity", 1)
                label = item.name + (f" ×{qty}" if qty > 1 else "")
                can_brew = item.key == "herbs" and hasattr(self, "can_brew_alchemy") and self.can_brew_alchemy()
                if can_brew:
                    brew_hint = "Press Enter to brew a potion"
                    rows.append({"key": item.key, "label": label, "detail": brew_hint, "action": "brew_alchemy", "color": item.color})
                else:
                    rows.append({"key": item.key, "label": label, "detail": "Sell at a town market for gold", "action": None, "color": item.color})
            elif item.category == "gem":
                qty = getattr(item, "quantity", 1)
                label = item.name + (f" ×{qty}" if qty > 1 else "")
                sell = GEMS.get(item.key, {}).get("sell", 3)
                rows.append({"key": item.key, "label": label, "detail": f"Gem — worth {sell}g at market", "action": None, "color": item.color})
            elif item.category == "curio":
                qty = getattr(item, "quantity", 1)
                label = item.name + (f" ×{qty}" if qty > 1 else "")
                sell = CURIOS.get(item.key, {}).get("sell", 2)
                rows.append({"key": item.key, "label": label, "detail": f"Curio — worth {sell}g at market", "action": None, "color": item.color})
            elif item.category == "locked_container":
                qty = getattr(item, "quantity", 1)
                label = item.name + (f" ×{qty}" if qty > 1 else "")
                diff = getattr(item, "lock_difficulty", 1)
                lp_rank = self.get_skill_rank("lockpicking") if hasattr(self, "get_skill_rank") else 0
                if lp_rank > 0:
                    detail = f"Lock difficulty {diff} — Press Enter to attempt (rank {lp_rank})"
                    action = "lockpick"
                else:
                    detail = f"Lock difficulty {diff} — take to a locksmith, or learn lockpicking"
                    action = None
                rows.append({"key": item.key, "label": label, "detail": detail, "action": action, "color": item.color})
            elif item.category == "quest":
                rows.append({"key": item.key, "label": item.name, "detail": "Quest item — cannot drop", "action": None, "color": item.color})
        has_trinket = any(item.category == "trinket" for item in self.inventory)
        if not has_trinket and getattr(self, "player_level", 1) < 2:
            rows.append({"key": "__trinket_locked__", "label": "Trinket Slot (Locked)", "detail": "Unlocks at Level 2 — Seasoned", "action": None, "color": (100, 90, 70), "locked": True})
        return rows

    def inventory_activate_selected(self):
        rows = self.inventory_rows()
        if not rows or self.inventory_index >= len(rows):
            return
        row = rows[self.inventory_index]
        if row["action"] is None:
            self.message = f"{row['label']}: {row['detail']}"
        elif row["action"] == "use":
            self.use_item(row["key"])
        elif row["action"] == "brew_alchemy":
            if hasattr(self, "brew_alchemy"):
                self.message = self.brew_alchemy("medkit")
        elif row["action"] == "lockpick":
            item = self.inventory_item(row["key"])
            if item and hasattr(self, "attempt_lockpick"):
                self.message = self.attempt_lockpick(item)
        else:
            self.equip_item(row["key"])
        self.inventory_index = min(self.inventory_index, max(0, len(self.inventory_rows()) - 1))

    def inventory_choice_from_screen(self, screen_x, screen_y):
        rows = self.inventory_rows()
        panel_width = 720
        left = (SCREEN_WIDTH - panel_width) // 2
        top = 136
        y = 20
        for index in range(len(rows)):
            row_rect = pygame.Rect(left + 12, top + y - 4, panel_width - 24, 30)
            if row_rect.collidepoint(screen_x, screen_y):
                return index
            y += 34
        return None

    def menu_choice_from_screen(self, screen_x, screen_y):
        if self.menu_mode == "controls":
            layout = self.controls_layout()
            if pygame.Rect(layout["back_left"], layout["back_top"], layout["back_width"], layout["back_height"]).collidepoint(screen_x, screen_y):
                return 0
            return None
        if self.menu_mode == "load":
            layout = self.load_layout()
            if pygame.Rect(layout["back_left"], layout["back_top"], layout["back_width"], layout["back_height"]).collidepoint(screen_x, screen_y):
                return len(self.save_entries)
            content_top_abs = layout["top"] + layout["content_top"]
            if content_top_abs <= screen_y < content_top_abs + layout["content_visible_h"]:
                row_i = (screen_y - content_top_abs) // layout["row_h"]
                save_idx = self.menu_scroll + row_i
                if 0 <= save_idx < len(self.save_entries):
                    return save_idx
            return None
        layout = self.menu_layout()
        box_width = layout["box_width"]
        box_height = layout["box_height"]
        start_y = layout["start_y"]
        gap = layout["gap"]
        left = layout["left"]
        visible_options = layout["visible_options"]
        scroll = layout["scroll"]
        for visible_index in range(len(visible_options)):
            top = start_y + visible_index * (box_height + gap)
            option = visible_options[visible_index]
            if option == "Load Game" and self.menu_mode == "main" and not has_save():
                continue
            if pygame.Rect(left, top, box_width, box_height).collidepoint(screen_x, screen_y):
                return scroll + visible_index
        return None

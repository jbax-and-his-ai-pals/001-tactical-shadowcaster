from __future__ import annotations

import random

from ..constants import COLOR_ACCENT, COLOR_HEAL, COLOR_ITEM_ARMOR, COLOR_ITEM_WEAPON
from ..item_catalog import ITEM_CATALOG, TRADER_COMMON, TRADER_UNCOMMON
from ..item_generation import compute_item_level, generate_armor, generate_weapon
from ..item_generation_data import QUALITY_TIERS
from ..loot_catalog import GEMS, CURIOS
from ..models import Item
from ..game_typing import GameMixinBase

# How many world-map steps before a town's stock refreshes
_STOCK_REFRESH_STEPS = 20

_HARVEST_SELL_PRICES: dict[str, int] = {
    "grain": 3,
    "herbs": 4,
    "ore":   5,
}
_WEAPON_GOLD_COSTS: dict[str, int] = {
    "dagger":    18,
    "shortbow":  12,
    "longbow":   24,
    "warhammer": 30,
    "spear":     30,
    "halberd":   48,
}
_ARMOR_GOLD_COSTS: dict[str, int] = {
    "travel_cloak":  12,
    "leather_armor": 24,
    "chain_mail":    36,
    "plate_coat":    48,
    "war_plate":     60,
}

# Trader base gold pool and attitude bonus per tier
_TRADER_BASE_GOLD = 80
_TRADER_ATTITUDE_BONUS = 30


class TradeMixin(GameMixinBase):

    def open_trade(self):
        self.stop_auto_movement()
        self.trade_open = True
        self.trade_panel = 0  # 0 = trader stock, 1 = player pack
        self.trade_stock_index = 0
        self.trade_pack_index = 0
        coord = self.world_position
        steps = getattr(self, "world_steps", 0)
        stock_steps = getattr(self, "trader_stock_steps", {})
        last_refresh = stock_steps.get(coord, -_STOCK_REFRESH_STEPS)
        if not self.trader_stock or steps - last_refresh >= _STOCK_REFRESH_STEPS:
            self._build_trader_stock()
            stock_steps[coord] = steps
            self.trader_stock_steps = stock_steps
        self.message = "The provisioner spreads the goods. Tab to switch panel, Enter to buy or sell."

    def close_trade(self):
        self.trade_open = False
        self.trader_stock = []
        self.trader_gold = 0

    def _attitude_tier(self):
        attitude = self.town_attitude_score() if hasattr(self, "town_attitude_score") else 0
        if attitude >= 8:
            return 2
        if attitude >= 3:
            return 1
        return 0

    def _shop_ilvl_cap(self) -> int:
        """Maximum item level this shop will generate based on player level + attitude + bartering."""
        level = getattr(self, "player_level", 1)
        attitude = self.town_attitude_score() if hasattr(self, "town_attitude_score") else 0
        level_cap = level * 2
        attitude_bonus = min(4, attitude // 2)
        barter_bonus = self.skill_shop_ilvl_bonus() if hasattr(self, "skill_shop_ilvl_bonus") else 0
        return min(15, level_cap + attitude_bonus + barter_bonus)

    def _trader_gold_pool(self):
        tier = self._attitude_tier()
        with self.seed_scope("trader_gold", self.world_position):
            base = _TRADER_BASE_GOLD + random.randint(-10, 10)
        return base + tier * _TRADER_ATTITUDE_BONUS

    def _build_trader_stock(self):
        supply_depth = getattr(self, "_supply_depth", 0)
        discount = self._trade_discount()
        ilvl_cap = self._shop_ilvl_cap()

        stock: list[dict] = []

        # Always available: common consumables from catalog
        for key in TRADER_COMMON:
            spec = ITEM_CATALOG[key]
            buy_price = spec.get("buy_price", 10)
            if buy_price <= 0:
                continue
            stock.append({"type": "consumable", "key": key, "name": spec["name"],
                           "price": max(1, buy_price - discount), "qty": 3})
        stock.append({"type": "ammo_bundle", "key": "ammo_bundle", "name": "Ammo (×5)",
                       "price": max(1, 12 - discount), "qty": 3})

        # Gear: seeded generated equipment with shop iLvl cap
        gear_items = self._trader_gear_offer(ilvl_cap)
        for item in gear_items:
            markup = 1.4 if item.quality in ("quality", "masterwork") else 1.2 if item.quality == "superior" else 1.0
            price = max(1, int(item.sell_price * markup) - discount * 2)
            stock.append({"type": "generated_gear", "key": item.key, "name": item.name,
                           "price": price, "item": item})

        # At supply depth 1+: uncommon consumables (biome-matched)
        if supply_depth >= 1:
            biome = self.region_type
            with self.seed_scope("trader_uncommon", self.world_position, ilvl_cap):
                uncommon_candidates = [
                    key for key in TRADER_UNCOMMON
                    if not ITEM_CATALOG[key]["biomes"] or biome in ITEM_CATALOG[key]["biomes"]
                ]
                if not uncommon_candidates:
                    uncommon_candidates = TRADER_UNCOMMON[:]
                for key in random.sample(uncommon_candidates, min(2, len(uncommon_candidates))):
                    spec = ITEM_CATALOG[key]
                    stock.append({"type": "consumable", "key": key, "name": spec["name"],
                                   "price": max(1, (spec.get("buy_price", 18) or 18) - discount), "qty": 2,
                                   "rarity": "uncommon"})

        # Crafting recipes appear when player has ingredients
        if self.inventory_quantity("grain") >= 2:
            stock.append({"type": "craft", "key": "craft_rations",
                           "name": "Pack Rations", "label": "2 grain → healing potion"})
        if self.inventory_quantity("herbs") >= 2:
            stock.append({"type": "craft", "key": "craft_tonic",
                           "name": "Brew Tonic", "label": "2 herbs → ward tonic"})
        if self.inventory_quantity("ore") >= 1:
            stock.append({"type": "craft", "key": "craft_ammo",
                           "name": "Forge Heads", "label": "1 ore → +2 ammo"})

        self.trader_stock = stock
        self.trader_gold = self._trader_gold_pool()
        self.trade_stock_index = min(self.trade_stock_index, max(0, len(stock) - 1))

    def _trade_discount(self):
        supply_depth = getattr(self, "_supply_depth", 0)
        attitude_tier = self._attitude_tier()
        discount = 0
        if supply_depth >= 3 or attitude_tier >= 2:
            discount = 3
        elif supply_depth >= 1 or attitude_tier >= 1:
            discount = 1
        discount += self.skill_buy_discount() if hasattr(self, "skill_buy_discount") else 0
        return discount

    def _trader_gear_offer(self, ilvl_cap: int) -> list:
        """Generate 2–4 pieces of equipment for the shop, seeded by town + ilvl_cap."""
        supply_depth = getattr(self, "_supply_depth", 0)
        slot_count = 2 + supply_depth  # 2 base, up to 4 at depth 2
        items = []
        with self.seed_scope("trader_offer", self.world_position, ilvl_cap):
            rng = random.Random(random.getrandbits(32))
            for i in range(slot_count):
                ilvl = min(ilvl_cap, max(1, rng.randint(1, ilvl_cap)))
                gen_fn = generate_weapon if i % 2 == 0 else generate_armor
                data = gen_fn(rng, ilvl)
                item = Item(
                    key=data["key"], name=data["name"], category=data["category"],
                    color=data["color"], marker=data["marker"], description=data["description"],
                    melee_bonus=data.get("melee_bonus", 0), ranged_bonus=data.get("ranged_bonus", 0),
                    defense_bonus=data.get("defense_bonus", 0),
                    max_hp_bonus=data.get("max_hp_bonus", 0), fov_bonus=data.get("fov_bonus", 0),
                    speed_bonus=data.get("speed_bonus", 0), range_bonus=data.get("range_bonus", 0),
                    ranged_penalty=data.get("ranged_penalty", 0), fov_penalty=data.get("fov_penalty", 0),
                    on_kill_heal=data.get("on_kill_heal", 0), low_hp_melee_bonus=data.get("low_hp_melee_bonus", 0),
                    sell_price=data.get("sell_price", 1), quality=data.get("quality", "normal"),
                    prefix_key=data.get("prefix_key"), suffix_key=data.get("suffix_key"),
                    base_key=data.get("base_key", ""), item_level=data.get("item_level", 0),
                    on_hit_effect=data.get("on_hit_effect", {}), passive_effects=data.get("passive_effects", {}),
                )
                items.append(item)
        return items

    def trade_switch_panel(self):
        self.trade_panel = 1 - self.trade_panel

    def trade_move_stock(self, delta):
        count = len(self.trader_stock)
        if count:
            self.trade_stock_index = (self.trade_stock_index + delta) % count

    def trade_move_pack(self, delta):
        rows = self._trade_pack_rows()
        if rows:
            self.trade_pack_index = (self.trade_pack_index + delta) % len(rows)

    def _trade_pack_rows(self):
        rows = []
        for item in self.inventory:
            if item.category in ("weapon", "armor", "consumable", "harvest", "gem", "curio"):
                rows.append(item)
        return rows

    def _item_sell_price(self, item) -> int:
        if item.category == "consumable":
            spec = ITEM_CATALOG.get(item.key)
            if spec:
                return spec.get("sell_price", 5)
            return 5
        if item.category == "harvest":
            return _HARVEST_SELL_PRICES.get(item.key, 2)
        if item.category == "weapon":
            if item.sell_price > 0:
                return item.sell_price
            return _WEAPON_GOLD_COSTS.get(item.base_key or item.key, 20) // 2
        if item.category == "armor":
            if item.sell_price > 0:
                return item.sell_price
            return _ARMOR_GOLD_COSTS.get(item.base_key or item.key, 20) // 2
        if item.category == "gem":
            return GEMS.get(item.key, {}).get("sell", 3) + (self.skill_sell_bonus() if hasattr(self, "skill_sell_bonus") else 0)
        if item.category == "curio":
            return CURIOS.get(item.key, {}).get("sell", 2) + (self.skill_sell_bonus() if hasattr(self, "skill_sell_bonus") else 0)
        return 1

    def trade_buy(self):
        stock = self.trader_stock
        if not stock:
            return
        idx = self.trade_stock_index
        if idx >= len(stock):
            return
        entry = stock[idx]

        if entry["type"] == "craft":
            self._apply_craft(entry["key"])
            # Rebuild stock in case ingredients ran out
            self._build_trader_stock()
            return

        price = entry.get("price", 0)
        if self.gold < price:
            self.message = f"You need {price}g for that. (You have {self.gold}g.)"
            return

        key = entry["key"]
        if entry["type"] == "consumable":
            if entry.get("qty", 0) <= 0:
                self.message = "Out of stock."
                return
            entry["qty"] -= 1
            self.gold -= price
            name = entry["name"]
            self.add_catalog_item(key, quantity=1)
            self.message = f"Bought {name} for {price}g. Gold: {self.gold}g."

        elif entry["type"] == "ammo_bundle":
            if entry.get("qty", 0) <= 0:
                self.message = "Out of stock."
                return
            entry["qty"] -= 1
            self.gold -= price
            self.ammo += 5
            self.message = f"Bought 5 ammo for {price}g. Ammo: {self.ammo}. Gold: {self.gold}g."

        elif entry["type"] == "generated_gear":
            item = entry.get("item")
            if item is None:
                return
            self.gold -= price
            self.inventory.append(item)
            self.message = f"Bought {item.name} for {price}g. Open inventory to equip. Gold: {self.gold}g."

    def _apply_craft(self, craft_key):
        if craft_key == "craft_rations":
            grain = self.inventory_item("grain")
            if grain is None or grain.quantity < 2:
                self.message = "You need 2 grain to pack rations."
                return
            grain.quantity -= 2
            if grain.quantity <= 0:
                self.inventory.remove(grain)
            self.add_item("medkit", "Healing Potion", "consumable", COLOR_HEAL, "vitality",
                          quantity=1, description="Restores health.")
            self.message = f"Packed field rations. +1 healing potion. Kits: {self.inventory_quantity('medkit')}."

        elif craft_key == "craft_tonic":
            herbs = self.inventory_item("herbs")
            if herbs is None or herbs.quantity < 2:
                self.message = "You need 2 herbs to brew a tonic."
                return
            herbs.quantity -= 2
            if herbs.quantity <= 0:
                self.inventory.remove(herbs)
            self.add_item("tonic", "Ward Tonic", "consumable", COLOR_ACCENT, "power",
                          quantity=1, description="Clears statuses and grants ward.")
            self.message = f"Brewed a ward tonic. +1 tonic. Tonics: {self.inventory_quantity('tonic')}."

        elif craft_key == "craft_ammo":
            ore = self.inventory_item("ore")
            if ore is None or ore.quantity < 1:
                self.message = "You need ore to forge arrowheads."
                return
            ore.quantity -= 1
            if ore.quantity <= 0:
                self.inventory.remove(ore)
            self.ammo += 2
            self.message = f"Forged broadheads from ore. +2 ammo. Ammo: {self.ammo}."

    def trade_sell(self):
        rows = self._trade_pack_rows()
        if not rows:
            self.message = "Nothing to sell."
            return
        idx = self.trade_pack_index
        if idx >= len(rows):
            return
        item = rows[idx]

        if item.equipped:
            self.message = f"{item.name} is equipped. Unequip it in your inventory first."
            return

        sell_price = self._item_sell_price(item)
        if self.trader_gold < sell_price:
            self.message = f"The trader can't afford {item.name} right now ({sell_price}g)."
            return

        qty = item.quantity if hasattr(item, "quantity") and item.quantity > 1 else 1

        if item.category in ("consumable", "harvest", "gem", "curio") and qty > 1:
            # Sell one at a time
            item.quantity -= 1
            if item.quantity <= 0:
                self.inventory.remove(item)
            self.gold += sell_price
            self.trader_gold -= sell_price
            self.message = f"Sold 1 {item.name} for {sell_price}g. Gold: {self.gold}g."
        else:
            self.inventory.remove(item)
            self.gold += sell_price
            self.trader_gold -= sell_price
            self.message = f"Sold {item.name} for {sell_price}g. Gold: {self.gold}g."

        # Keep cursor in bounds
        rows_after = self._trade_pack_rows()
        if rows_after:
            self.trade_pack_index = min(self.trade_pack_index, len(rows_after) - 1)
        else:
            self.trade_pack_index = 0

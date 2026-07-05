from __future__ import annotations

import random

from ..constants import COLOR_ACCENT, COLOR_HEAL, COLOR_ITEM_ARMOR, COLOR_ITEM_WEAPON
from ..item_catalog import ITEM_CATALOG, TRADER_COMMON, TRADER_UNCOMMON
from ..game_typing import GameMixinBase

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
        self._build_trader_stock()
        self.message = "The provisioner spreads the goods. Tab to switch panel, Enter to buy or sell."

    def close_trade(self):
        self.trade_open = False
        self.trader_stock = []
        self.trader_gold = 0

    def _attitude_tier(self):
        attitude = getattr(self, "town_attitude", {}).get(self.world_position, 0)
        if attitude >= 8:
            return 2
        if attitude >= 3:
            return 1
        return 0

    def _trader_gold_pool(self):
        tier = self._attitude_tier()
        with self.seed_scope("trader_gold", self.world_position):
            base = _TRADER_BASE_GOLD + random.randint(-10, 10)
        return base + tier * _TRADER_ATTITUDE_BONUS

    def _build_trader_stock(self):
        supply_depth = getattr(self, "_supply_depth", 0)
        attitude_tier = self._attitude_tier()
        discount = self._trade_discount()

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

        # Gear: seeded offer per town
        weapon_key, armor_key = self._trader_gear_offer()
        if weapon_key:
            w_price = max(1, _WEAPON_GOLD_COSTS.get(weapon_key, 20) - discount * 2)
            weapon_name = self.WEAPON_CATALOG[weapon_key]["name"]
            stock.append({"type": "weapon", "key": weapon_key, "name": weapon_name, "price": w_price})
        if armor_key:
            a_price = max(1, _ARMOR_GOLD_COSTS.get(armor_key, 20) - discount * 2)
            armor_name = self.ARMOR_CATALOG[armor_key]["name"]
            stock.append({"type": "armor", "key": armor_key, "name": armor_name, "price": a_price})

        # At supply depth 1+: uncommon consumables (biome-matched)
        if supply_depth >= 1:
            biome = self.region_type
            with self.seed_scope("trader_uncommon", self.world_position):
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

        # At supply depth 1+, offer a second weapon and armor
        if supply_depth >= 1:
            weapon_key2, armor_key2 = self._trader_gear_offer(offset=1)
            if weapon_key2 and weapon_key2 != weapon_key:
                w_price2 = max(1, _WEAPON_GOLD_COSTS.get(weapon_key2, 20) - discount * 2)
                stock.append({"type": "weapon", "key": weapon_key2,
                               "name": self.WEAPON_CATALOG[weapon_key2]["name"], "price": w_price2})
            if armor_key2 and armor_key2 != armor_key:
                a_price2 = max(1, _ARMOR_GOLD_COSTS.get(armor_key2, 20) - discount * 2)
                stock.append({"type": "armor", "key": armor_key2,
                               "name": self.ARMOR_CATALOG[armor_key2]["name"], "price": a_price2})

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
        return discount

    def _trader_gear_offer(self, offset=0):
        weapon_keys = sorted(self.WEAPON_CATALOG.keys())
        armor_keys = sorted(self.ARMOR_CATALOG.keys())
        with self.seed_scope("trader_offer", self.world_position, offset):
            weapon_key = random.choice(weapon_keys)
            armor_key = random.choice(armor_keys)
        return weapon_key, armor_key

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
            if item.category in ("weapon", "armor", "consumable", "harvest"):
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
            return _WEAPON_GOLD_COSTS.get(item.key, 20) // 2
        if item.category == "armor":
            return _ARMOR_GOLD_COSTS.get(item.key, 20) // 2
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

        elif entry["type"] == "weapon":
            catalog = self.WEAPON_CATALOG.get(key)
            if not catalog:
                return
            if self.owns_item(key):
                self.message = f"You already own {catalog['name']}."
                return
            self.gold -= price
            self.add_item(key, catalog["name"], "weapon", catalog["color"], "weapon",
                          melee_bonus=catalog["melee_bonus"], ranged_bonus=catalog["ranged_bonus"],
                          description=catalog.get("description", ""))
            self.message = f"Bought {catalog['name']} for {price}g. Open inventory to equip. Gold: {self.gold}g."

        elif entry["type"] == "armor":
            catalog = self.ARMOR_CATALOG.get(key)
            if not catalog:
                return
            if self.owns_item(key):
                self.message = f"You already own {catalog['name']}."
                return
            self.gold -= price
            self.add_item(key, catalog["name"], "armor", catalog["color"], "armor",
                          defense_bonus=catalog["defense_bonus"], description=catalog.get("description", ""))
            self.message = f"Bought {catalog['name']} for {price}g. Open inventory to equip. Gold: {self.gold}g."

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

        if item.category in ("consumable", "harvest") and qty > 1:
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

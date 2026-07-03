from __future__ import annotations

from ..game_typing import GameMixinBase


class TuningMixin(GameMixinBase):
    @staticmethod
    def default_tuning():
        return {
            "heal_pickup_floor_interval": 3,
            "heal_pickup_restore": 1,
            "heal_pickup_require_missing_hp": 1,
            "full_explore_vitality_bonus": 1,
            "full_explore_power_bonus": 1,
            "full_explore_recovery_medkits": 1,
            "full_explore_recovery_tonics": 1,
            "medkit_heal": 4,
            "bottom_reward_ammo": 2,
            "bottom_reward_medkits": 2,
            "delve_reward_vitality_bonus": 3,
            "delve_reward_power_bonus": 1,
            "delve_reward_recovery_tonics": 1,
            "vitality_upgrade_amount": 2,
            "power_upgrade_amount": 1,
            "light_upgrade_amount": 1,
            "haste_upgrade_amount": 8,
            "reach_upgrade_amount": 1,
            "completion_modal_duration_ms": 1500,
            "enemy_status_duration": 3,
            "shaman_poison_duration": 1,
        }

    @staticmethod
    def tuner_schema():
        return [
            {"key": "heal_pickup_floor_interval", "label": "Heal pickup every N floors", "min": 1, "max": 6, "step": 1},
            {"key": "heal_pickup_restore", "label": "Heal pickup restore", "min": 1, "max": 6, "step": 1},
            {"key": "heal_pickup_require_missing_hp", "label": "Require missing HP for spawn", "min": 0, "max": 1, "step": 1},
            {"key": "full_explore_vitality_bonus", "label": "100% vitality bonus", "min": 1, "max": 4, "step": 1},
            {"key": "full_explore_power_bonus", "label": "100% power bonus", "min": 1, "max": 3, "step": 1},
            {"key": "full_explore_recovery_medkits", "label": "100% reward medkits", "min": 0, "max": 3, "step": 1},
            {"key": "full_explore_recovery_tonics", "label": "100% reward tonics", "min": 0, "max": 3, "step": 1},
            {"key": "medkit_heal", "label": "Medkit healing", "min": 1, "max": 10, "step": 1},
            {"key": "enemy_status_duration", "label": "Enemy status duration", "min": 1, "max": 5, "step": 1},
            {"key": "shaman_poison_duration", "label": "Shaman poison duration", "min": 1, "max": 4, "step": 1},
            {"key": "bottom_reward_ammo", "label": "Delve reward: recovery ammo", "min": 0, "max": 5, "step": 1},
            {"key": "bottom_reward_medkits", "label": "Delve reward: recovery medkits", "min": 0, "max": 4, "step": 1},
            {"key": "delve_reward_vitality_bonus", "label": "Delve reward: vitality bonus", "min": 1, "max": 6, "step": 1},
            {"key": "delve_reward_power_bonus", "label": "Delve reward: power bonus", "min": 1, "max": 3, "step": 1},
            {"key": "delve_reward_recovery_tonics", "label": "Delve reward: recovery tonics", "min": 0, "max": 3, "step": 1},
            {"key": "vitality_upgrade_amount", "label": "Vitality upgrade HP", "min": 1, "max": 6, "step": 1},
            {"key": "power_upgrade_amount", "label": "Power upgrade damage", "min": 1, "max": 4, "step": 1},
            {"key": "light_upgrade_amount", "label": "Light upgrade radius", "min": 1, "max": 4, "step": 1},
            {"key": "haste_upgrade_amount", "label": "Haste upgrade (ms per pickup)", "min": 2, "max": 15, "step": 1},
            {"key": "reach_upgrade_amount", "label": "Reach upgrade (tiles per pickup)", "min": 1, "max": 2, "step": 1},
            {"key": "completion_modal_duration_ms", "label": "Popup duration (ms)", "min": 900, "max": 3000, "step": 100},
        ]

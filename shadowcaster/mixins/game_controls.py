from __future__ import annotations

from ..game_typing import GameMixinBase
from ..constants import (
    ACTION_AUTOEXPLORE,
    ACTION_CLEANSE,
    ACTION_DESCEND,
    ACTION_HEAL,
    ACTION_INVENTORY,
    ACTION_JOURNAL,
    ACTION_LOG,
    ACTION_MELEE,
    ACTION_RANGED,
    ACTION_WORLD_MAP,
    COLOR_ACCENT, COLOR_HEAL, COLOR_STAIRS, COLOR_TEXT,
    SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, VIEW_HEIGHT, VIEW_WIDTH,
)


class ControlsMixin(GameMixinBase):

    def controls_tabs(self):
        return ["Keyboard / Mouse", "Controller"]

    def shift_controls_tab(self, delta):
        tabs = self.controls_tabs()
        self.controls_tab = (self.controls_tab + delta) % len(tabs)

    def set_controls_tab(self, index):
        self.controls_tab = max(0, min(len(self.controls_tabs()) - 1, index))

    def current_controls_scroll(self):
        return self.controls_scroll[self.controls_tab]

    def controls_content_rect(self):
        layout = self.controls_layout()
        return {
            "left": 22,
            "top": 68,
            "width": layout["box_width"] - 44,
            "height": layout["box_height"] - 88,
        }

    def controls_layout(self):
        box_width = 700
        box_height = 410
        left = (SCREEN_WIDTH - box_width) // 2
        top = 210
        back_width = 220
        back_height = 52
        back_left = (SCREEN_WIDTH - back_width) // 2
        back_top = top + box_height + 18
        return {
            "box_width": box_width,
            "box_height": box_height,
            "left": left,
            "top": top,
            "back_width": back_width,
            "back_height": back_height,
            "back_left": back_left,
            "back_top": back_top,
        }

    def active_controller_name(self):
        if not self.controller_present():
            return ""
        controller = self.controllers.get(self.active_controller_id)
        return controller.get_name() if controller else ""

    def controller_family(self):
        name = self.active_controller_name().lower()
        if "playstation" in name or "dualshock" in name or "dualsense" in name or "ps4" in name or "ps5" in name:
            return "playstation"
        if "switch" in name or "joy-con" in name or "pro controller" in name or "nintendo" in name:
            return "nintendo"
        if "xbox" in name or "xinput" in name:
            return "xbox"
        return "generic"

    def controller_button_labels(self):
        family = self.controller_family()
        if family == "playstation":
            return {
                "confirm": "Cross",
                "back": "Circle",
                "ranged": "Square",
                "autoexplore": "Triangle",
                "left_shoulder": "L1",
                "right_shoulder": "R1",
                "world_map": "Create / Share",
                "menu": "Options",
                "tuner": "R3",
                "move": "Left Stick or D-pad",
                "family_label": "PlayStation-style",
            }
        if family == "nintendo":
            return {
                "confirm": "B",
                "back": "A",
                "ranged": "Y",
                "autoexplore": "X",
                "left_shoulder": "L",
                "right_shoulder": "R",
                "world_map": "-",
                "menu": "+",
                "tuner": "R Stick",
                "move": "Left Stick or D-pad",
                "family_label": "Nintendo-style",
            }
        if family == "xbox":
            return {
                "confirm": "A",
                "back": "B",
                "ranged": "X",
                "autoexplore": "Y",
                "left_shoulder": "LB",
                "right_shoulder": "RB",
                "world_map": "View",
                "menu": "Menu",
                "tuner": "R Stick",
                "move": "Left Stick or D-pad",
                "family_label": "Xbox-style",
            }
        return {
            "confirm": "Face South",
            "back": "Face East",
            "ranged": "Face West",
            "autoexplore": "Face North",
            "left_shoulder": "Left Shoulder",
            "right_shoulder": "Right Shoulder",
            "world_map": "Back / View",
            "menu": "Menu / Start",
            "tuner": "Right Stick Click",
            "move": "Left Stick or D-pad",
            "family_label": "Generic layout",
        }

    def controls_sections(self):
        controller_labels = self.controller_button_labels()
        if self.controls_tab == 0:
            return [
                (
                    "Movement",
                    [
                        "Move: arrows or WASD",
                        "Diagonals: Q E Z C or numpad 7 9 1 3",
                        "Hold a movement key to keep walking",
                        "Autoexplore this floor: X",
                        "Numpad quick keys: 5 attack, 0 auto, . use, + kit, - tonic, * shot, / map",
                    ],
                ),
                (
                    "Actions",
                    [
                        "Melee attack or talk nearby: Space",
                        "Ranged attack: F",
                        "Medkit: H",
                        "Tonic: G",
                        "Use stairs, portal, or exit: Enter or .",
                    ],
                ),
                (
                    "Navigation",
                    [
                        "World map: M",
                        "Inventory: I",
                        "Journal: J",
                        "Recent log: L",
                        "Balance tuner during a run: T",
                        "Menu: Esc",
                        "Switch controls tabs here: Left/Right, Q/E, or Tab",
                    ],
                ),
                (
                    "Mouse",
                    [
                        "Hover or click visible creatures, items, exits, and landmarks to inspect",
                        "Click seen tiles to path when no hostile is visible",
                        "Click a landmark to walk into it if the route is safe",
                    ],
                ),
            ]
        family_line = f"Shown in {controller_labels['family_label']} terms."
        if self.active_controller_name():
            family_line = f"{family_line} Detected: {self.active_controller_name()}."
        return [
            (
                "Movement",
                [
                    f"Move: {controller_labels['move']}",
                    "Push diagonally on the stick or D-pad for diagonal travel",
                    "Hold a direction to keep walking",
                    f"Switch controls tabs here: {controller_labels['left_shoulder']} / {controller_labels['right_shoulder']}",
                ],
            ),
            (
                "Actions",
                [
                    f"Melee attack or talk nearby: {controller_labels['confirm']}",
                    f"Ranged attack: {controller_labels['ranged']}",
                    f"Autoexplore: {controller_labels['autoexplore']}",
                    f"Medkit: {controller_labels['left_shoulder']}",
                    f"Tonic: {controller_labels['right_shoulder']}",
                    f"Back or cancel: {controller_labels['back']}",
                ],
            ),
                (
                "Navigation",
                [
                    f"World map: {controller_labels['world_map']}",
                    "On world map — D-pad or Left Stick moves selection; X/Square scrolls detail up; Y/Triangle scrolls detail down; LB/RB switches mode",
                    f"Menu: {controller_labels['menu']}",
                    "Inventory, Journal, and Log: open the pause menu, then choose them there",
                    f"Tuner during a run: {controller_labels['tuner']}",
                    family_line,
                ],
            ),
            (
                "Notes",
                [
                    "Button names can vary across controller families even when the in-game actions are the same",
                    "If your controller uses different labels, match the same face-button directions instead",
                ],
            ),
        ]

    def wrap_line_count(self, text, width):
        words = text.split()
        if not words:
            return 1
        count = 1
        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            if self.small_font.size(trial)[0] <= width:
                current = trial
            else:
                count += 1
                current = word
        return count

    def controls_content_height(self):
        rect = self.controls_content_rect()
        line_width = rect["width"] - 32
        height = 0
        for _, lines in self.controls_sections():
            height += 26
            for line in lines:
                height += self.wrap_line_count(line, line_width) * 20
            height += 10
        return height

    def controls_max_scroll(self):
        return max(0, self.controls_content_height() - self.controls_content_rect()["height"] + 8)

    def scroll_controls(self, delta):
        index = self.controls_tab
        self.controls_scroll[index] = max(0, min(self.controls_max_scroll(), self.controls_scroll[index] + delta))

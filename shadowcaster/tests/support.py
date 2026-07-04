from __future__ import annotations

import os


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from shadowcaster.game import Game


_DISPLAY_READY = False


def ensure_pygame():
    global _DISPLAY_READY
    if _DISPLAY_READY:
        return
    pygame.init()
    pygame.display.set_mode((100, 100))
    _DISPLAY_READY = True


def make_game(seed: int | None = None) -> Game:
    ensure_pygame()
    game = Game()
    if seed is not None:
        game.config_world_seed = seed
        game.world_seed = seed
    return game

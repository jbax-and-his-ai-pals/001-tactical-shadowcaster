import random

from .constants import MAX_LEAF_SIZE, MIN_LEAF_SIZE, MIN_ROOM_SIZE
from .models import RectRoom


class Leaf:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.left: "Leaf | None" = None
        self.right: "Leaf | None" = None
        self.room: RectRoom | None = None

    def split(self):
        if self.left or self.right:
            return False

        split_h = random.choice([True, False])
        if self.w / self.h >= 1.25:
            split_h = False
        elif self.h / self.w >= 1.25:
            split_h = True

        max_split = (self.h if split_h else self.w) - MIN_LEAF_SIZE
        if max_split <= MIN_LEAF_SIZE:
            return False

        split = random.randint(MIN_LEAF_SIZE, max_split)
        if split_h:
            self.left = Leaf(self.x, self.y, self.w, split)
            self.right = Leaf(self.x, self.y + split, self.w, self.h - split)
        else:
            self.left = Leaf(self.x, self.y, split, self.h)
            self.right = Leaf(self.x + split, self.y, self.w - split, self.h)
        return True

    def create_rooms(self, dungeon):
        if self.left or self.right:
            if self.left:
                self.left.create_rooms(dungeon)
            if self.right:
                self.right.create_rooms(dungeon)
            if self.left and self.right:
                left_room = self.left.get_room()
                right_room = self.right.get_room()
                if left_room and right_room:
                    dungeon.create_corridor(left_room.center, right_room.center)
            return

        room_w = random.randint(MIN_ROOM_SIZE, max(MIN_ROOM_SIZE, self.w - 2))
        room_h = random.randint(MIN_ROOM_SIZE, max(MIN_ROOM_SIZE, self.h - 2))
        room_x = random.randint(self.x + 1, self.x + self.w - room_w - 1)
        room_y = random.randint(self.y + 1, self.y + self.h - room_h - 1)
        self.room = RectRoom(room_x, room_y, room_w, room_h)
        dungeon.carve_room(self.room)

    def get_room(self):
        if self.room:
            return self.room

        rooms = []
        if self.left:
            left_room = self.left.get_room()
            if left_room:
                rooms.append(left_room)
        if self.right:
            right_room = self.right.get_room()
            if right_room:
                rooms.append(right_room)
        return random.choice(rooms) if rooms else None


class Dungeon:
    def __init__(self, width, height):
        self.width: int = width
        self.height: int = height
        self.tiles: list[list[int]] = [[1 for _ in range(height)] for _ in range(width)]
        self.rooms: list[RectRoom] = []
        self.metadata: dict = {}
        self.transparent_tiles: set[tuple[int, int]] = set()
        self.generate()

    def generate(self):
        root = Leaf(1, 1, self.width - 2, self.height - 2)
        leaves = [root]
        did_split = True
        while did_split:
            did_split = False
            for leaf in leaves[:]:
                if leaf.left or leaf.right:
                    continue
                if leaf.w > MAX_LEAF_SIZE or leaf.h > MAX_LEAF_SIZE or random.random() > 0.25:
                    if leaf.split():
                        leaves.extend(child for child in (leaf.left, leaf.right) if child is not None)
                        did_split = True
        root.create_rooms(self)

    def carve_room(self, room):
        self.rooms.append(room)
        for x in range(room.x, room.x + room.w):
            for y in range(room.y, room.y + room.h):
                self.tiles[x][y] = 0

    def create_corridor(self, start, end):
        x1, y1 = start
        x2, y2 = end
        if random.choice([True, False]):
            self.carve_h_tunnel(x1, x2, y1)
            self.carve_v_tunnel(y1, y2, x2)
        else:
            self.carve_v_tunnel(y1, y2, x1)
            self.carve_h_tunnel(x1, x2, y2)

    def carve_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y] = 0

    def carve_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y] = 0

    def is_blocked(self, x, y):
        return not (0 <= x < self.width and 0 <= y < self.height) or self.tiles[x][y] == 1

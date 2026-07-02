import heapq
from collections import deque


def blocks_sight(dungeon, x, y):
    transparent_tiles = getattr(dungeon, "transparent_tiles", set())
    return dungeon.is_blocked(x, y) and (x, y) not in transparent_tiles


def cast_light(cx, cy, row, start_slope, end_slope, radius, xx, xy, yx, yy, dungeon, visible):
    if start_slope < end_slope:
        return
    radius_squared = radius * radius
    blocked = False
    next_start_slope = start_slope
    distance = row
    while distance <= radius and not blocked:
        delta_y = -distance
        delta_x = -distance
        while delta_x <= 0:
            current_x = cx + delta_x * xx + delta_y * xy
            current_y = cy + delta_x * yx + delta_y * yy
            left_slope = (delta_x - 0.5) / (delta_y + 0.5)
            right_slope = (delta_x + 0.5) / (delta_y - 0.5)
            if start_slope < right_slope:
                delta_x += 1
                continue
            if end_slope > left_slope:
                break
            if 0 <= current_x < dungeon.width and 0 <= current_y < dungeon.height and delta_x * delta_x + delta_y * delta_y <= radius_squared:
                visible.add((current_x, current_y))
            tile_is_wall = blocks_sight(dungeon, current_x, current_y)
            if blocked:
                if tile_is_wall:
                    next_start_slope = right_slope
                else:
                    blocked = False
                    start_slope = next_start_slope
            elif tile_is_wall and distance < radius:
                blocked = True
                cast_light(cx, cy, distance + 1, start_slope, left_slope, radius, xx, xy, yx, yy, dungeon, visible)
                next_start_slope = right_slope
            delta_x += 1
        distance += 1


def compute_fov(px, py, radius, dungeon):
    visible = {(px, py)}
    transforms = [
        (1, 0, 0, 1),
        (0, 1, 1, 0),
        (0, -1, 1, 0),
        (-1, 0, 0, 1),
        (-1, 0, 0, -1),
        (0, -1, -1, 0),
        (0, 1, -1, 0),
        (1, 0, 0, -1),
    ]
    for xx, xy, yx, yy in transforms:
        cast_light(px, py, 1, 1.0, 0.0, radius, xx, xy, yx, yy, dungeon, visible)
    return visible


def heuristic(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def direction_toward(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    return (0 if dx == 0 else (1 if dx > 0 else -1), 0 if dy == 0 else (1 if dy > 0 else -1))


def can_step(dungeon, start, destination):
    x, y = destination
    if dungeon.is_blocked(x, y):
        return False
    dx = x - start[0]
    dy = y - start[1]
    if abs(dx) > 1 or abs(dy) > 1 or (dx == 0 and dy == 0):
        return False
    return True


def find_path(dungeon, start, goal, occupied=None, allowed_tiles=None, tile_costs=None):
    occupied = occupied or set()
    tile_costs = tile_costs or {}
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            neighbor = (current[0] + dx, current[1] + dy)
            if not can_step(dungeon, current, neighbor):
                continue
            if allowed_tiles is not None and neighbor not in allowed_tiles and neighbor != goal:
                continue
            if neighbor in occupied and neighbor != goal:
                continue
            new_cost = cost_so_far[current] + 1 + tile_costs.get(neighbor, 0)
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(goal, neighbor)
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current
    if goal not in came_from:
        return []
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path


def flood_reachable_tiles(dungeon, start):
    if dungeon.is_blocked(*start):
        return set()
    reachable = {start}
    frontier = deque([start])
    while frontier:
        current = frontier.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor in reachable:
                continue
            if not can_step(dungeon, current, neighbor):
                continue
            reachable.add(neighbor)
            frontier.append(neighbor)
    return reachable

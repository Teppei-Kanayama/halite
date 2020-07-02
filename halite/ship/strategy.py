import numpy as np

from halite.ship.ship_utils import decide_direction, calculate_distance


# haliteが多い方向を探して向かう
def decide_direction_for_rich_position(board, ship, size, safe_directions, percentile_threshold, search_width):
    threshold = np.percentile([cell.halite for cell in board.cells.values()], percentile_threshold)
    search_range = [((ship.position[0] + i) % size, (ship.position[0] + j) % size) for i in range(search_width) for j in range(search_width)]
    target_map = {pos: board.cells[pos].halite for pos in search_range if board.cells[pos].halite >= threshold}
    if target_map:
        destination = min(target_map.keys(), key=lambda x: calculate_distance(x, ship.position, size))
        return decide_direction(safe_directions, ship.position, destination, size)
    return np.random.choice(safe_directions)


# 「responsive_areaの中」かつ「閾値以上のhaliteがある」positionの中で最も近いpositionに向かう
def decide_direction_in_responsive_area(board, ship, size, safe_directions, responsive_area, halite_threshold):
    halite_thresholds = [100, 50, 25, 5, 0]
    for halite_threshold in halite_thresholds:
        candidate_positions = [pos for pos in responsive_area if board.cells[pos].halite >= halite_threshold]
        if candidate_positions:
            destination = min(candidate_positions, key=lambda x: calculate_distance(x, ship.position, size))
            return decide_direction(safe_directions, ship.position, destination, size)
    return np.random.choice(safe_directions)


# 自分より重い敵の中で最も近い敵に向かう
def attack_heavy_nearest_ship(ship, size, safe_directions, enemy_ship_positions):
    my_halite = ship.halite
    heavier_enemy_ship_positions = {k: v for k, v in enemy_ship_positions.items() if v > my_halite}
    if heavier_enemy_ship_positions:
        destination = min(heavier_enemy_ship_positions.keys(), key=lambda x: calculate_distance(x, ship.position, size))
        return decide_direction(safe_directions, ship.position, destination, size)
    return np.random.choice(safe_directions)


# 最も近くにある敵のshipyardに向かう
def attack_enemy_shipyard(ship, size, safe_directions, enemy_shipyard_positions):
    if enemy_shipyard_positions:
        destination = min(enemy_shipyard_positions, key=lambda x: calculate_distance(x, ship.position, size))
        return decide_direction(safe_directions, ship.position, destination, size)
    return np.random.choice(safe_directions)


# 最も近くにある自分のshipyardに向かう
def decide_direction_for_shipyard(ally_shipyard_positions, my_position, safe_directions, size):
    destination = min(ally_shipyard_positions, key=lambda x: calculate_distance(x, my_position, size))
    return decide_direction(safe_directions, my_position, destination, size)


# 固定の優先順位にしたがって移動する
def decide_direction_by_fixed_priority(safe_directions):
    priority = dict(north=1, east=1, south=-1, west=-1, stay=0)
    safe_directions_with_priority = {k: v for k, v in priority.items() if k in safe_directions}
    return  max(safe_directions_with_priority.items(), key=lambda x: x[1])[0]

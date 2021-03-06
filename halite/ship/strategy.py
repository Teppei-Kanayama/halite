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
def decide_direction_in_responsive_area(board, my_position, size, safe_directions, responsive_area, halite_thresholds):
    for halite_threshold in halite_thresholds:
        candidate_positions = [pos for pos in responsive_area if board.cells[pos].halite >= halite_threshold]
        if candidate_positions:
            destination = min(candidate_positions, key=lambda x: calculate_distance(x, my_position, size))
            return decide_direction(safe_directions, my_position, destination, size)
    return np.random.choice(safe_directions)


# 優先度1（MUST）：自分より重いこと
# 優先度2：ターゲットであること
# 優先度3：最も近いこと
def attack_heavy_target_ship(safe_directions, enemy_ship_positions, my_halite, my_position, enemy_ship_ids, target_enemy_id, size):
    heavier_enemy_ship_positions = {k: v for k, v in enemy_ship_positions.items() if v > my_halite}
    heavier_target_enemy_ship_positions = {pos: halite for pos, halite in heavier_enemy_ship_positions.items() if enemy_ship_ids[pos] == target_enemy_id}
    if heavier_target_enemy_ship_positions:
        return attack_nearest_ship(safe_directions, heavier_target_enemy_ship_positions, my_position, size)
    if heavier_enemy_ship_positions:
        return attack_nearest_ship(safe_directions, enemy_ship_positions, my_position, size)
    return np.random.choice(safe_directions)


# 優先度1（MUST）：自分より重いこと
# 優先度2：ターゲットであること
# 優先度3：距離N以内であること
# 優先度4：最も重いこと
def attack_heavy_target_ship2(safe_directions, enemy_ship_halites, my_halite, my_position, enemy_ship_ids, target_enemy_id, size):
    heavier_enemy_ship_positions = {k: v for k, v in enemy_ship_halites.items() if v > my_halite}
    heavier_target_enemy_ship_positions = {pos: halite for pos, halite in heavier_enemy_ship_positions.items() if enemy_ship_ids[pos] == target_enemy_id}
    heavier_target_close_enemy_ship_positions = {pos: halite for pos, halite in heavier_target_enemy_ship_positions.items()
                                                 if calculate_distance(pos, my_position, size) <= 100}
    if heavier_target_close_enemy_ship_positions:
        return attack_heaviest_ship(safe_directions, heavier_target_close_enemy_ship_positions, my_position, size)
    if heavier_target_enemy_ship_positions:
        return attack_heaviest_ship(safe_directions, heavier_target_enemy_ship_positions, my_position, size)
    if heavier_enemy_ship_positions:
        return attack_nearest_ship(safe_directions, enemy_ship_halites, my_position, size)
    return np.random.choice(safe_directions)


# 最も重い的に向かう
def attack_heaviest_ship(safe_directions, enemy_ship_positions, my_position, size):
    destination = max(enemy_ship_positions.items(), key=lambda x: x[1])[0]
    return decide_direction(safe_directions, my_position, destination, size)


# 最も近い敵に向かう
# TODO: attack nearsest target として一般化できそう
def attack_nearest_ship(safe_directions, enemy_ship_positions, my_position, size):
    destination = min(enemy_ship_positions.keys(), key=lambda x: calculate_distance(x, my_position, size))
    return decide_direction(safe_directions, my_position, destination, size)


def attack_target_shipyard(target_enemy_id, my_position, size, safe_directions_without_shipyards, enemy_shipyard_ids):
    target_enemy_shipyard_positions = [shipyard_position for shipyard_position, player_id in enemy_shipyard_ids.items() if player_id == target_enemy_id]
    if target_enemy_shipyard_positions:
        return attack_nearest_shipyard(my_position, size, safe_directions_without_shipyards, target_enemy_shipyard_positions)
    return None


# 最も近くにある敵のshipyardに向かう
# TODO: attack nearsest target として一般化できそう
def attack_nearest_shipyard(my_position, size, safe_directions, enemy_shipyard_positions):
    destination = min(enemy_shipyard_positions, key=lambda x: calculate_distance(x, my_position, size))
    return decide_direction(safe_directions, my_position, destination, size)


# 最も近くにある自分のshipyardに向かう
def decide_direction_for_shipyard(ally_shipyard_ids, my_position, safe_directions, size):
    destination = min(ally_shipyard_ids.keys(), key=lambda x: calculate_distance(x, my_position, size))
    return decide_direction(safe_directions, my_position, destination, size)


# 固定の優先順位にしたがって移動する
def decide_direction_by_fixed_priority(safe_directions):
    priority = dict(north=1, east=1, south=-1, west=-1, stay=0)
    safe_directions_with_priority = {k: v for k, v in priority.items() if k in safe_directions}
    return  max(safe_directions_with_priority.items(), key=lambda x: x[1])[0]

from typing import Tuple, List

import numpy as np

from halite.ship.ship_utils import decide_direction, calculate_distance, \
    decide_direction_toward_multiple_position_options


# 優先度1 (MUST): responsive_areaの中であること
# 優先度2 (複数候補あり): 閾値以上のhaliteがあること
# 優先度3: 最も近いこと
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
def attack_heavy_target_ship(safe_directions, enemy_ship_halites, my_halite, my_position, enemy_ship_ids, target_enemy_id, size):
    heavier_enemy_ship_positions = {k: v for k, v in enemy_ship_halites.items() if v > my_halite}
    heavier_target_enemy_ship_positions = {pos: halite for pos, halite in heavier_enemy_ship_positions.items() if enemy_ship_ids[pos] == target_enemy_id}
    if heavier_target_enemy_ship_positions:
        return decide_direction_toward_multiple_position_options(my_position=my_position,
                                                                 destination_chioice=list(heavier_target_enemy_ship_positions.keys()),
                                                                 safe_directions=safe_directions, size=size)
    if heavier_enemy_ship_positions:
        return decide_direction_toward_multiple_position_options(my_position=my_position,
                                                                 destination_chioice=list(heavier_enemy_ship_positions.keys()),
                                                                 safe_directions=safe_directions, size=size)
    return np.random.choice(safe_directions)


# 優先度1（MUST）：自分より重いこと
# 優先度2：ターゲットであること
# 優先度3：距離 distance_threshold 以内であること
# 優先度4：最も重いこと
def attack_heavy_target_ship2(safe_directions, enemy_ship_halites, my_halite, my_position, enemy_ship_ids, target_enemy_id, size, distance_threshold: int = 100):
    heavier_enemy_ship_positions = {k: v for k, v in enemy_ship_halites.items() if v > my_halite}
    heavier_target_enemy_ship_positions = {pos: halite for pos, halite in heavier_enemy_ship_positions.items() if enemy_ship_ids[pos] == target_enemy_id}
    heavier_target_close_enemy_ship_positions = {pos: halite for pos, halite in heavier_target_enemy_ship_positions.items()
                                                 if calculate_distance(pos, my_position, size) <= distance_threshold}
    if heavier_target_close_enemy_ship_positions:
        return attack_heaviest_ship(safe_directions=safe_directions, enemy_ship_positions=heavier_target_close_enemy_ship_positions,
                                    my_position=my_position, size=size)
    if heavier_target_enemy_ship_positions:
        return attack_heaviest_ship(safe_directions=safe_directions, enemy_ship_positions=heavier_target_enemy_ship_positions,
                                    my_position=my_position, size=size)
    if heavier_enemy_ship_positions:
        return decide_direction_toward_multiple_position_options(my_position=my_position,
                                                                 destination_chioice=list(heavier_enemy_ship_positions.keys()),
                                                                 safe_directions=safe_directions, size=size)
    return np.random.choice(safe_directions)


# 最も重い的に向かう
# attack_heavy_target_ship2の補助関数
def attack_heaviest_ship(safe_directions, enemy_ship_positions, my_position, size):
    destination = max(enemy_ship_positions.items(), key=lambda x: x[1])[0]
    return decide_direction(safe_directions, my_position, destination, size)


# 敵のshipyardに向かう
# 優先度1 (MUST)：ターゲットであること
def attack_target_shipyard(target_enemy_id, my_position, size, safe_directions_without_shipyards, enemy_shipyard_ids):
    target_enemy_shipyard_positions = [shipyard_position for shipyard_position, player_id in enemy_shipyard_ids.items() if player_id == target_enemy_id]
    if target_enemy_shipyard_positions:
        return decide_direction_toward_multiple_position_options(my_position=my_position,
                                                                 destination_chioice=list(target_enemy_shipyard_positions),
                                                                 safe_directions=safe_directions_without_shipyards, size=size)
    return None


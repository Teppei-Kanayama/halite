from typing import Tuple, Optional, Dict, List


# pos1からpos2に行くのにかかる歩数を計算する
import numpy as np


def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int], size: int):
    distance_x = min((pos1[0] - pos2[0]) % size, (pos2[0] - pos1[0]) % size)
    distance_y = min((pos1[1] - pos2[1]) % size, (pos2[1] - pos1[1]) % size)
    return distance_x + distance_y


# from_positionからto_positionに行きたい場合に、各方向に点数をつける
# 近くなら1, 遠ざかるなら-1, 変わらないなら0
def get_direction_to_destination(from_position, to_position, size):
    scores = dict(north=0, south=0, east=0, west=0, stay=0)
    from_x = from_position[0]
    from_y = from_position[1]
    to_x = to_position[0]
    to_y = to_position[1]

    if (from_x == to_x) & (from_y == to_y):
        scores['stay'] += 1
        return scores

    if (from_x - to_x) % size > (to_x - from_x) % size:
        scores['east'] += 1
        scores['west'] -= 1
    elif (from_x - to_x) % size < (to_x - from_x) % size:
        scores['west'] += 1
        scores['east'] -= 1

    if (from_y - to_y) % size > (to_y - from_y) % size:
        scores['north'] += 1
        scores['south'] -= 1
    elif (from_y - to_y) % size < (to_y - from_y) % size:
        scores['south'] += 1
        scores['north'] -= 1

    return scores


# from_positionからto_positionへ行きたい場合に具体的に進むべき方向を出力する
# safe_directionsのなかで、get_direction_to_destinationで得られたスコアが最大の方向に進む
def decide_direction(safe_directions, from_position, to_position, size):
    direction_scores = get_direction_to_destination(from_position, to_position, size=size)
    safe_direction_scores = {k: v for k, v in direction_scores.items() if k in safe_directions}
    return max(safe_direction_scores, key=safe_direction_scores.get)


# 他のshipより近くにあるpositionを列挙する
# key: ship_id
# value: positionのlist
def get_nearest_areas(ships, size: int) -> Optional[Dict[str, List[Tuple[int, int]]]]:
    if len(ships) == 0:
        return None

    responsive_areas = {ship.id: [] for ship in ships}
    for x in range(size):
        for y in range(size):
            distance_dict = {ship.id: calculate_distance((x, y), ship.position, size) for ship in ships}
            responsive_ship_id = min(distance_dict, key=distance_dict.get)  # TODO: 先頭の負担が大きい
            responsive_areas[responsive_ship_id].append((x, y))
    return responsive_areas


# 全体の盤面におけるhaliteのpercentileを計算する
def calculate_halite_percentile(board, percentile):
    return np.percentile([cell.halite for cell in board.cells.values()], percentile)

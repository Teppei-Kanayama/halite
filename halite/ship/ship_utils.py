import numpy as np


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


def calculate_distance(pos1, pos2, size):
    distance_x = min((pos1[0] - pos2[0]) % size, (pos2[0] - pos1[0]) % size)
    distance_y = min((pos1[1] - pos2[1]) % size, (pos2[1] - pos1[1]) % size)
    return distance_x + distance_y


def decide_direction(safe_directions, current_position, destination, size):
    direction_scores = get_direction_to_destination(current_position, destination, size=size)
    safe_direction_scores = {k: v for k, v in direction_scores.items() if k in safe_directions}
    if safe_direction_scores:
        return max(safe_direction_scores, key=safe_direction_scores.get)
    return None


def decide_direction_for_rich_position(board, ship, size, safe_directions):
    threshold = np.percentile([cell.halite for cell in board.cells.values()], 85)
    search_range = [((ship.position[0] + i) % size, (ship.position[0] + j) % size) for i in range(5) for j in range(5)]
    target_map = {pos: board.cells[pos].halite for pos in search_range if board.cells[pos].halite >= threshold}

    def calculate_distance(target):
        distance_x = min((target[0] - ship.position[0]) % size, (ship.position[0] - target[0]) % size)
        distance_y = min((target[1] - ship.position[1]) % size, (ship.position[1] - target[1]) % size)
        return distance_x + distance_y

    if target_map:
        destination = min(target_map.keys(), key=calculate_distance)
        return decide_direction(safe_directions, ship.position, destination, size)
    return None

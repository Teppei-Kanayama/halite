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
    # return decide_direction_by_fixed_priority(safe_directions)
    return np.random.choice(safe_directions)

# shipyardに向かう
def decide_direction_for_shipyard(me, ship, safe_directions, size):
    destination = np.random.choice(me.shipyards).position  # TODO: 一番近いshipyardsに帰る
    return decide_direction(safe_directions, ship.position, destination, size)


# 固定の優先順位にしたがって移動する
def decide_direction_by_fixed_priority(safe_directions):
    priority = dict(north=1, east=1, south=-1, west=-1, stay=0)
    safe_directions_with_priority = {k: v for k, v in priority.items() if k in safe_directions}
    return  max(safe_directions_with_priority.items(), key=lambda x: x[1])[0]

import numpy as np

from halite.ship.ship_utils import decide_direction


# haliteが多い方向を探して向かう
# 十分多くのhaliteが見つからなければrandomで移動する
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
    return np.random.choice(safe_directions)  # TODO: 1方向に定める


# shipyardに向かう
def decide_direction_for_shipyard(me, ship, safe_directions, size):
    destination = np.random.choice(me.shipyards).position  # TODO: 一番近いshipyardsに帰る
    return decide_direction(safe_directions, ship.position, destination, size)

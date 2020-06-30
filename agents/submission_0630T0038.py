from kaggle_environments.envs.halite.helpers import *



# TODO: shipごとにいくつかのstrategyを混ぜていきたい
def decide_one_ship_action(ship, me, board, size, safe_directions: List[Tuple[int, int]], already_convert: bool):
    # 動ける場所がないなら動かない
    if len(safe_directions) == 0:
        return None

    # 下記の条件を満たす場合shipyardにconvertする
    # shipyardsが少ない・haliteが十分にある・stayが安全である・まだこのターンにconvertしていない
    if len(me.shipyards) <= min((board.step // 80), 1) and me.halite >= 500 and 'stay' in safe_directions and not already_convert:
        return ShipAction.CONVERT

    # その場にhaliteがたくさんあるなら拾う
    if ship.cell.halite > 100 and 'stay' in safe_directions:
        return None

    # haliteをたくさん載せているならshipyardsに帰る
    if ship.halite > 500 and len(me.shipyards) > 0:
        direction = decide_direction_for_shipyard(me, ship, safe_directions, size)
        return direction_mapper[direction]

    # haliteを探す
    direction = decide_direction_for_rich_position(board, ship, size, safe_directions, percentile_threshold=85, search_width=5)
    return direction_mapper[direction]


def decide_ship_actions(me, board, size):
    actions = {}
    fixed_positions = []
    already_convert = False
    for ship in me.ships:
        my_position = ship.position
        my_halite = ship.halite
        ally_ship_positions = {ship.position: ship.halite for ship in me.ships if ship.position != my_position}
        enemy_ship_positions = {ship.position: ship.halite for ship in board.ships.values()
                                if (ship.position not in list(ally_ship_positions.keys())) and (ship.position != my_position)}
        ally_shipyard_positions = [shipyard.position for shipyard in me.shipyards]
        enemy_shipyard_positions = [shipyard.position for shipyard in board.shipyards.values() if shipyard.position not in ally_shipyard_positions]
        action_manager = ActionManager(my_position=my_position,
                                       my_halite=my_halite,
                                       ally_ship_positions=ally_ship_positions,
                                       enemy_ship_positions=enemy_ship_positions,
                                       ally_shipyard_positions=ally_shipyard_positions,
                                       enemy_shipyard_positions=enemy_shipyard_positions,
                                       size=size,
                                       fixed_positions=fixed_positions)
        safe_directions = action_manager.get_action_options()
        action = decide_one_ship_action(ship, me, board, size, safe_directions, already_convert)
        add_fixed_position(fixed_positions, action, my_position, size)
        if action:
            actions[ship.id] = action
        if action == ShipAction.CONVERT:
            already_convert = True
    return actions


def add_fixed_position(fixed_positions, action, my_position, size) -> None:
    if action == ShipAction.CONVERT:
        return
    if action is None:
        fixed_positions.append(my_position)
        return
    next_vector = direction_vector[action_to_direction[action]]
    next_position = ((my_position[0] + next_vector[0]) % size, (my_position[1] + next_vector[1]) % size)
    fixed_positions.append(next_position)
    return
from typing import Dict, Tuple, List




class ActionManager:
    def __init__(self, my_position: Tuple[int, int], my_halite: int, ally_ship_positions: Dict[Tuple[int, int], int],
                 enemy_ship_positions: Dict[Tuple[int, int], int], ally_shipyard_positions: List[Tuple[int, int]],
                 enemy_shipyard_positions: List[Tuple[int, int]], size: int, fixed_positions: List[Tuple[int, int]]):
        self._my_position = my_position
        self._my_halite = my_halite
        self._ally_ship_positions = ally_ship_positions
        self._enemy_ship_positions = enemy_ship_positions
        self._ally_shipyard_positions = ally_shipyard_positions
        self._enemy_shipyard_positions = enemy_shipyard_positions
        self._size = size
        self._fixed_positions = fixed_positions

    def get_action_options(self):
        dangerous_positions = self._get_dangerous_positions(enemy_ship_positions=self._enemy_ship_positions,
                                                            enemy_shipyard_positions=self._enemy_shipyard_positions,
                                                            fixed_positions=self._fixed_positions,
                                                            size=self._size)
        safe_directions = self._get_safe_directions(dangerous_positions=dangerous_positions,
                                                    my_position=self._my_position,
                                                    size=self._size)
        return safe_directions

    @staticmethod
    def _get_dangerous_positions(enemy_ship_positions: Dict[Tuple[int, int], int], enemy_shipyard_positions: List[Tuple[int, int]],
                                 fixed_positions: List[Tuple[int, int]], size: int) -> List[Tuple[int, int]]:
        dangerous_positions = []

        # enemy ship
        # TODO: 相手のhaliteが自分よりも多ければ安全
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for pos in enemy_ship_positions.keys():
            dangerous_positions.append(pos)
            for dir in directions:
                dangerous_positions.append(((pos[0] + dir[0]) % size, (pos[1] + dir[1]) % size))

        # my ship
        dangerous_positions += fixed_positions

        # enemy shipyard
        for pos in enemy_shipyard_positions:
            dangerous_positions.append(pos)

        return dangerous_positions

    @staticmethod
    def _get_safe_directions(dangerous_positions: List[Tuple[int, int]], my_position: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        safe_directions = []
        for direction, vector in direction_vector.items():
            target_x = (my_position[0] + vector[0]) % size
            target_y = (my_position[1] + vector[1]) % size
            if (target_x, target_y) not in dangerous_positions:
                safe_directions.append(direction)
        return safe_directions
import numpy as np



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
# pos1からpos2に行くのにかかる歩数を計算する
def calculate_distance(pos1, pos2, size):
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
import numpy as np
from kaggle_environments.envs.halite.helpers import ShipyardAction


def decide_shipyard_actions(me, board, ship_actions):
    # とりあえず数が少なかったらランダムにspawnする
    # TODO: shipが乗っているタイミングではspawnしない
    if len(me.ships) <= 6 and len(me.shipyards) > 0 and me.halite >= 1000:
        target_shipyard = np.random.choice(me.shipyards)
        return {target_shipyard.id: ShipyardAction.SPAWN}
    return {}
from kaggle_environments.envs.halite.helpers import ShipAction

direction_mapper = dict(north=ShipAction.NORTH, east=ShipAction.EAST, south=ShipAction.SOUTH, west=ShipAction.WEST, stay=None)
direction_vector = dict(north=(0, 1), east=(1, 0),  south=(0, -1), west=(-1, 0), stay=(0, 0))
action_to_direction = {ShipAction.NORTH: 'north', ShipAction.EAST:'east', ShipAction.SOUTH: 'south', ShipAction.WEST: 'west'}

from kaggle_environments.envs.halite.helpers import *



def agent(obs, config):
    size = config.size
    board = Board(obs, config)
    me = board.current_player

    ship_actions = decide_ship_actions(me, board, size)
    for ship_id, action in ship_actions.items():
        board.ships[ship_id].next_action = action

    shipyard_actions = decide_shipyard_actions(me, board, ship_actions)
    for shipyard_id, action in shipyard_actions.items():
        board.shipyards[shipyard_id].next_action = action

    return me.next_actions

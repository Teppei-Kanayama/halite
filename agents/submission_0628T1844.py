from kaggle_environments.envs.halite.helpers import *
import numpy as np

from halite.ship.action_manager import ActionManager
from halite.ship.ship_utils import get_direction_to_destination
from halite.utils.constants import direction_mapper


def decide_one_ship_action(ship, me, board, size, already_convert):
    # 動いていい場所を消める
    action_manager = ActionManager(ship, board, me, size)
    safe_directions = action_manager.get_action_options()

    # 動ける場所がないなら動かない
    if len(safe_directions) == 0:
        return None, already_convert

    # 条件を満たす場合convertする
    # shipyardsが少ない・haliteが十分にある・stayが安全である・まだこのターンにconvertしていない
    if len(me.shipyards) < 1 and me.halite >= 500 and 'stay' in safe_directions and not already_convert:
        return ShipAction.CONVERT, True

    # その場にhaliteがたくさんあるなら拾う
    if ship.cell.halite > 100 and 'stay' in safe_directions:
        return None, already_convert

    # haliteをたくさん載せているならshipyardsに帰る
    if ship.halite > 500 and len(me.shipyards) > 0:
        destination = np.random.choice(me.shipyards).position  # TODO: 一番近いshipyardsに帰る
        direction_scores = get_direction_to_destination(ship.position, destination, size=size)
        safe_direction_scores = {k: v for k, v in direction_scores.items() if k in safe_directions}
        if len(safe_direction_scores) > 0:
            direction = max(safe_direction_scores, key=safe_direction_scores.get)
            if direction == 'stay':
                return None, already_convert
            return direction_mapper[direction], already_convert

    # 探索範囲内で閾値以上のhaliteがある地点のうち、最も近い地点に移動する
    threshold = np.percentile([cell.halite for cell in board.cells.values()], 85)
    search_range = [((ship.position[0] + i) % size, (ship.position[0] + j) % size) for i in range(5) for j in range(5)]
    target_map = {pos: board.cells[pos].halite for pos in search_range if board.cells[pos].halite >= threshold}

    def calculate_distance(target):
        distance_x = min((target[0] - ship.position[0]) % size, (ship.position[0] - target[0]) % size)
        distance_y = min((target[1] - ship.position[1]) % size, (ship.position[1] - target[1]) % size)
        return distance_x + distance_y

    if target_map:
        destination = min(target_map.keys(), key=calculate_distance)
        direction_scores = get_direction_to_destination(ship.position, destination, size=size)
        safe_direction_scores = {k: v for k, v in direction_scores.items() if k in safe_directions}
        if len(safe_direction_scores) > 0:
            direction = max(safe_direction_scores, key=safe_direction_scores.get)
            if direction == 'stay':
                return None, already_convert
            return direction_mapper[direction], already_convert

    # その他ならランダムに移動する
    direction = np.random.choice(safe_directions)
    if direction == 'stay':
        return None, already_convert
    return direction_mapper[direction], already_convert


def decide_ship_actions(me, board, size):
    actions = {}
    already_convert = False
    for ship in me.ships:
        action, already_convert = decide_one_ship_action(ship, me, board, size, already_convert)
        if action:
            actions[ship.id] = action
    return actions
import copy


class ActionManager:
    def __init__(self, ship, board, me, size):
        self._ship = ship
        self._board = board
        self._me = me
        self._size = size

    def get_action_options(self):
        ship_positions = [s.position for s in self._board.ships.values()]
        # TODO: spawnしたタイミングで衝突しうる
        shipyard_positions = [s.position for k, s in self._board.shipyards.items() if not f'-{self._me.id + 1}' in k]
        my_position = self._ship.position
        dangerous_positions = self._get_dangerous_positions(ship_positions, shipyard_positions, my_position, self._size)
        safe_directions = self._get_safe_directions(dangerous_positions, my_position, self._size)
        return safe_directions

    @staticmethod
    def _get_dangerous_positions(ship_positions, shipyard_positions, my_position, size=21):
        dangerous_positions = []

        # ship
        ship_positions = copy.copy(ship_positions)
        ship_positions.remove(my_position)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for pos in ship_positions:
            dangerous_positions.append(pos)
            for dir in directions:
                dangerous_positions.append(((pos[0] + dir[0]) % size, (pos[1] + dir[1]) % size))

        # shipyard
        for pos in shipyard_positions:
            dangerous_positions.append(pos)

        return dangerous_positions

    @staticmethod
    def _get_safe_directions(dangerous_positions, my_position, size=21):
        safe_directions = []
        directions = dict(east=(1, 0), west=(-1, 0), north=(0, 1), south=(0, -1), stay=(0, 0))
        for direction, diff in directions.items():
            target_x = (my_position[0] + diff[0]) % size
            target_y = (my_position[1] + diff[1]) % size
            if (target_x, target_y) not in dangerous_positions:
                safe_directions.append(direction)
        return safe_directions
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
import numpy as np
from kaggle_environments.envs.halite.helpers import ShipyardAction


def decide_shipyard_actions(me, board):
    # とりあえず数が少なかったらランダムにspawnする
    if len(me.ships) <= min((board.step // 40), 4) and len(me.shipyards) > 0 and me.halite >= 1000:
        target_shipyard = np.random.choice(me.shipyards)
        return {target_shipyard.id: ShipyardAction.SPAWN}
    return {}
from kaggle_environments.envs.halite.helpers import ShipAction

direction_mapper = dict(north=ShipAction.NORTH, east=ShipAction.EAST, south=ShipAction.SOUTH, west=ShipAction.WEST)
from kaggle_environments.envs.halite.helpers import *

from halite.ship.decide_ship_actions import decide_ship_actions
from halite.shipyard.decide_shipyard_actions import decide_shipyard_actions


def agent(obs, config):
    size = config.size
    board = Board(obs, config)
    me = board.current_player

    ship_actions = decide_ship_actions(me, board, size)
    for ship_id, action in ship_actions.items():
        board.ships[ship_id].next_action = action

    shipyard_actions = decide_shipyard_actions(me, board)
    for shipyard_id, action in shipyard_actions.items():
        board.shipyards[shipyard_id].next_action = action

    return me.next_actions

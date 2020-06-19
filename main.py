from kaggle_environments.envs.halite.helpers import *
import numpy as np
import random
import copy


def getDirTo(fromPos, toPos, size):
    fromX, fromY = divmod(fromPos[0],size), divmod(fromPos[1],size)
    toX, toY = divmod(toPos[0],size), divmod(toPos[1],size)
    if fromY < toY: return ShipAction.NORTH
    if fromY > toY: return ShipAction.SOUTH
    if fromX < toX: return ShipAction.EAST
    if fromX > toX: return ShipAction.WEST


# Directions a ship can move
direction_mapper = dict(north=ShipAction.NORTH, east=ShipAction.EAST, south=ShipAction.SOUTH, west=ShipAction.WEST)


class ActionManager:
    def __init__(self, ship, board, me, size):
        self._ship = ship
        self._board = board
        self._me = me
        self._size = size

    def get_action_options(self):
        ship_positions = [s.position for s in self._board.ships.values()]
        shipyard_positions = [s.position for k, s in self._board.shipyards.items() if not f'{self._me.id}-' in k]
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


def agent(obs, config):
    size = config.size
    board = Board(obs, config)
    me = board.current_player
    ship_states = {}

    # STEP1: shipyardがspawnするかどうかを決める
    # とりあえず数が少なかったらランダムにspawnする
    if len(me.ships) <= (board.step // 40) and len(me.shipyards) > 0 and me.halite >= 1000:
        target_shipyard = np.random.choice(me.shipyards)
        target_shipyard.next_action = ShipyardAction.SPAWN

    # STEP2: 動いていい場所を消める
    for ship in me.ships:
        action_manager = ActionManager(ship, board, me, size)
        safe_directions = action_manager.get_action_options()

    # STEP3: 目的地を決める
        direction = np.random.choice(safe_directions)
        # direction = safe_directions[0]
        if direction != 'stay':
            ship.next_action = direction_mapper[direction]

    return me.next_actions

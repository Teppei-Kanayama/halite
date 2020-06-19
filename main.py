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
    def __init__(self, ship, board):
        self._ship = ship
        self._board = board

    def get_action_options(self):
        ship_positions = [s.position for s in self._board.ships.values()]  # [(5, 15), (15, 15), (5, 5), (15, 5)]
        shipyard_positions = [s.position for s in self._board.shipyards.values()]
        my_position = self._ship.position  # (5, 15)
        dangerous_positions = self._get_dangerous_positions(ship_positions, shipyard_positions, my_position)
        safe_directions = self._get_safe_directions(dangerous_positions, my_position)
        return safe_directions

    @staticmethod
    def _get_dangerous_positions(ship_positions, shipyard_positions, my_position):
        dangerous_positions = []
        ship_positions = copy.copy(ship_positions)
        ship_positions.remove(my_position)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for pos in ship_positions:
            dangerous_positions.append(pos)
            for dir in directions:
                dangerous_positions.append(((pos[0] + dir[0]) % 21, (pos[1] + dir[1]) % 21))

        # TODO: shipyard
        return dangerous_positions

    @staticmethod
    def _get_safe_directions(dangerous_positions, my_position):
        safe_directions = []
        directions = dict(north=(0, -1), south=(0, 1), east=(1, 0), west=(-1, 0), stay=(0, 0))
        for direction, diff in directions.items():
            target_x = (my_position[0] + diff[0]) % 21
            target_y = (my_position[1] + diff[1]) % 21
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
        action_manager = ActionManager(ship, board)
        safe_directions = action_manager.get_action_options()

    # STEP3: 目的地を決める
        if ship.next_action is None:

            # Part 1: Set the ship's state
            if ship.halite <= 500:  # If cargo is too low, collect halite
                ship_states[ship.id] = "COLLECT"
            else:  # If cargo gets very big, deposit halite
                ship_states[ship.id] = "DEPOSIT"

            # Part 2: Use the ship's state to select an action
            if ship_states[ship.id] == "COLLECT":
                # If halite at current location running low,
                # move to the adjacent square containing the most halite
                if ship.cell.halite < 100:
                    neighbors = [ship.cell.north.halite, ship.cell.east.halite,
                                 ship.cell.south.halite, ship.cell.west.halite]
                    random.shuffle(neighbors)
                    if len(neighbors):
                        best = max(range(len(neighbors)), key=neighbors.__getitem__)
                        ship.next_action = directions[best]
            elif ship_states[ship.id] == "DEPOSIT":
                # Move towards shipyard to deposit cargo
                direction = getDirTo(ship.position, me.shipyards[0].position, size)
                if direction: ship.next_action = direction
            else:
                pass  # no chance

    return me.next_actions

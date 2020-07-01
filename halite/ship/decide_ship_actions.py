import heapq

import numpy as np
from kaggle_environments.envs.halite.helpers import *

from halite.ship.action_manager import ActionManager
from halite.ship.attacker import decide_attacker_action
from halite.ship.collector import decide_collector_action
from halite.ship.ship_utils import get_nearest_areas
from halite.utils.constants import action_to_direction, direction_vector


def manage_ship_roles(ships, board):
    # TODO: 3種類以上のrollに対応する
    # TODO: utilsに移動
    percentile = np.percentile([cell.halite for cell in board.cells.values()], 97)
    num_ships = len(ships)
    n_collector_ships = int(num_ships * min(max((percentile / 50 - 1), 0), 1))
    ship_halites = {ship.id: ship.halite for ship in ships}

    # TODO: refactor
    lists = heapq.nlargest(n_collector_ships, ship_halites.items(), key=lambda x: x[1])
    collector_ships = {}
    for l in lists:
        collector_ships[l[0]] = l[1]

    ship_roles = {}
    for ship in ships:
        ship_roles[ship.id] = 'collector' if ship.id in collector_ships.keys() else 'attacker'

    return ship_roles


def decide_ship_actions(me, board, size):
    actions = {}
    fixed_positions = []
    already_convert = False

    ship_roles = manage_ship_roles(me.ships, board)

    collection_ships = [ship for ship in me.ships if ship_roles[ship.id] == 'collector']
    responsive_areas = get_nearest_areas(collection_ships, size)

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
        if ship_roles[ship.id] == 'collector':
            responsive_area = responsive_areas[ship.id]
            action = decide_collector_action(ship, me, board, size, safe_directions, already_convert, responsive_area, enemy_ship_positions)
        elif ship_roles[ship.id] == 'attacker':
            action = decide_attacker_action(ship, me, board, size, safe_directions, already_convert, enemy_ship_positions, enemy_shipyard_positions)
        else:
            raise NotImplementedError

        add_fixed_position(fixed_positions, action, my_position, size)
        if action:
            actions[ship.id] = action
        if action == ShipAction.CONVERT:
            already_convert = True
    return actions, fixed_positions


# すでに行動が確定したshipの位置を保存する。
def add_fixed_position(fixed_positions: List[Tuple[int, int]], action: ShipAction, my_position: Tuple[int, int], size: int) -> None:
    if action == ShipAction.CONVERT:
        return
    if action is None:
        fixed_positions.append(my_position)
        return
    next_vector = direction_vector[action_to_direction[action]]
    next_position = ((my_position[0] + next_vector[0]) % size, (my_position[1] + next_vector[1]) % size)
    fixed_positions.append(next_position)
    return

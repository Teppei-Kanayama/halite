import heapq

import numpy as np
from kaggle_environments.envs.halite.helpers import *

from halite.ship.action_manager import ActionManager
from halite.ship.roll.attacker import decide_attacker_action
from halite.ship.roll.collector import decide_collector_action
from halite.ship.ship_utils import get_nearest_areas, calculate_halite_percentile
from halite.utils.constants import action_to_direction, direction_vector


def manage_ship_roles(ships, board):
    # TODO: 3種類以上のrollに対応する
    percentile = calculate_halite_percentile(board, 97)
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


def decide_target_enemy(board):
    asset_dict = dict()
    for player_id in board.players.keys():
        player = board.players[player_id]
        halite = player.halite
        cargo = np.array([ship.halite for ship in player.ships]).sum()
        total_asset = halite + cargo
        asset_dict[player_id] = total_asset

    my_asset = asset_dict[board.current_player.id]
    enemy_assets = {player_id: asset for player_id, asset in asset_dict.items() if player_id != board.current_player.id}
    richer_enemy_assets = {player_id: asset for player_id, asset in enemy_assets.items() if asset > my_asset}

    if richer_enemy_assets:
        target_enemy_id = min(richer_enemy_assets.items(), key=lambda x: x[1])[0]
        return target_enemy_id
    return min(enemy_assets.items(), key=lambda x: x[1])[0]


def decide_ship_actions(me, board, size):
    actions = {}
    fixed_positions = []
    already_convert = False  # TODO: convert_managerを作る

    ship_roles = manage_ship_roles(me.ships, board)

    collection_ships = [ship for ship in me.ships if ship_roles[ship.id] == 'collector']
    responsive_areas = get_nearest_areas(collection_ships, size)

    target_enemy_id = decide_target_enemy(board)

    for ship in me.ships:
        my_position = ship.position
        my_halite = ship.halite
        ally_ship_positions = {ship.position: ship.halite for ship in me.ships if ship.position != my_position}  # 自分含まない
        enemy_ship_positions = {ship.position: ship.halite for ship in board.ships.values()
                                if (ship.position not in list(ally_ship_positions.keys())) and (ship.position != my_position)}
        enemy_ship_ids = {ship.position: ship.id.split('-')[1] for ship in board.ships.values()
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

        safe_directions = action_manager.get_action_options(avoid_shipyards=True)
        safe_directions_without_shipyards = action_manager.get_action_options(avoid_shipyards=False)

        if ship_roles[ship.id] == 'collector':
            responsive_area = responsive_areas[ship.id]
            action_function = decide_collector_action
        elif ship_roles[ship.id] == 'attacker':
            responsive_area = None
            action_function = decide_attacker_action
        else:
            raise NotImplementedError

        action, log = action_function(ship, me, board, size, safe_directions, safe_directions_without_shipyards, already_convert,
                                      responsive_area, board.step,
                                      my_position, my_halite,
                                      ally_ship_positions, enemy_ship_positions, enemy_ship_ids, ally_shipyard_positions, enemy_shipyard_positions,
                                      target_enemy_id)
        print(board.step, ship.id, ship_roles[ship.id], target_enemy_id, log)
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

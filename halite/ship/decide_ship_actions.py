from kaggle_environments.envs.halite.helpers import *

from halite.ship.action_manager import ActionManager
from halite.ship.strategy import decide_direction_for_rich_position, decide_direction_for_shipyard
from halite.utils.constants import direction_mapper


# TODO: shipごとにいくつかのstrategyを混ぜていきたい
def decide_one_ship_action(ship, me, board, size, safe_directions, already_convert):
    # 動ける場所がないなら動かない
    if len(safe_directions) == 0:
        return None, already_convert

    # 下記の条件を満たす場合shipyardにconvertする
    # shipyardsが少ない・haliteが十分にある・stayが安全である・まだこのターンにconvertしていない
    if len(me.shipyards) <= min((board.step // 80), 1) and me.halite >= 500 and 'stay' in safe_directions and not already_convert:
        return ShipAction.CONVERT, True

    # その場にhaliteがたくさんあるなら拾う
    if ship.cell.halite > 100 and 'stay' in safe_directions:
        return None, already_convert

    # haliteをたくさん載せているならshipyardsに帰る
    if ship.halite > 500 and len(me.shipyards) > 0:
        direction = decide_direction_for_shipyard(me, ship, safe_directions, size)
        return direction_mapper[direction], already_convert

    # haliteを探す
    direction = decide_direction_for_rich_position(board, ship, size, safe_directions, percentile_threshold=85, search_width=5)
    return direction_mapper[direction], already_convert


def decide_ship_actions(me, board, size):
    actions = {}
    already_convert = False
    for ship in me.ships:
        # 動いていい場所を決める
        my_position = ship.position
        my_halite = ship.halite
        ally_ship_positions = {ship.position: ship.halite for ship in me.ships}
        enemy_ship_positions = {ship.position: ship.halite for ship in board.ships.values() if ship.position not in list(ally_ship_positions.keys())}
        ally_shipyard_positions = [shipyard.position for shipyard in me.shipyards]
        enemy_shipyard_positions = [shipyard.position for shipyard in board.shipyards.values() if shipyard.position not in ally_shipyard_positions]
        action_manager = ActionManager(my_position=my_position,
                                       my_halite=my_halite,
                                       ally_ship_positions=ally_ship_positions,
                                       enemy_ship_positions=enemy_ship_positions,
                                       ally_shipyard_positions=ally_shipyard_positions,
                                       enemy_shipyard_positions=enemy_shipyard_positions,
                                       size=size,
                                       other_ship_actions=actions)
        safe_directions = action_manager.get_action_options()
        action, already_convert = decide_one_ship_action(ship, me, board, size, safe_directions, already_convert)
        if action:
            actions[ship.id] = action
    return actions

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
        action_manager = ActionManager(ship, board, me, size)
        safe_directions = action_manager.get_action_options()  # TODO: safe_directionsの決定時に、ship間の連携ができるようにしたい
        action, already_convert = decide_one_ship_action(ship, me, board, size, safe_directions, already_convert)
        if action:
            actions[ship.id] = action
    return actions

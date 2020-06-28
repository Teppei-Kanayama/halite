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
    if len(me.shipyards) <= min((board.step // 80), 1) and me.halite >= 500 and 'stay' in safe_directions and not already_convert:
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

    # その他ならランダムに移動する
    # TODO: 探索の仕方を工夫する
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

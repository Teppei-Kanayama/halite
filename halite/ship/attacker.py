from kaggle_environments.envs.halite.helpers import *

from halite.ship.strategy import decide_direction_for_shipyard, attack_heavy_nearest_ship
from halite.utils.constants import direction_mapper


def decide_attacker_action(ship, me, board, size: int, safe_directions: List[Tuple[int, int]], already_convert: bool, enemy_ship_positions):
    GO_SHIPYARD_WHEN_CARGO_IS_OVER = 300

    # 「最終ターン」かつ「haliteを500以上積んでいる」ならばconvertする
    if board.step == 398 and ship.halite > 500:
        return ShipAction.CONVERT

    # 動ける場所がないなら動かない
    # TODO: ランダムに動いた方がいいかもしれない
    if len(safe_directions) == 0:
        return None

    # 「haliteをたくさん載せている」ならshipyardsに帰る
    if ship.halite > GO_SHIPYARD_WHEN_CARGO_IS_OVER and len(me.shipyards) > 0:
        direction = decide_direction_for_shipyard(me, ship, safe_directions, size)
        return direction_mapper[direction]

    direction = attack_heavy_nearest_ship(ship, size, safe_directions, enemy_ship_positions)
    return direction_mapper[direction]
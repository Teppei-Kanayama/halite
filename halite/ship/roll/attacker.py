import numpy as np
from kaggle_environments.envs.halite.helpers import *

from halite.ship.strategy import decide_direction_for_shipyard, attack_heavy_nearest_ship, attack_enemy_shipyard
from halite.utils.constants import direction_mapper


def decide_attacker_action(ship, me, board, size: int, safe_directions: List[Tuple[int, int]], already_convert: bool,
                           responsive_area: List[Tuple[int, int]], step: int, my_position, my_halite,
                           ally_ship_positions, enemy_ship_positions, ally_shipyard_positions, enemy_shipyard_positions) -> Tuple[Optional[ShipAction], str]:
    GO_SHIPYARD_WHEN_CARGO_IS_OVER = 300
    ATTACK_SHIPYARD_IS_LESS = 100

    # 「最終ターン」かつ「haliteを500以上積んでいる」ならばconvertする
    if step == 398 and my_halite > 500:
        return ShipAction.CONVERT, 'final convert'

    # 動ける場所がないならランダムに動く
    if len(safe_directions) == 0:
        return np.random.choice(safe_directions), 'nothing to do'

    # 「haliteをたくさん載せている」ならshipyardsに帰る
    if ship.halite > GO_SHIPYARD_WHEN_CARGO_IS_OVER and len(me.shipyards) > 0:
        direction = decide_direction_for_shipyard(me, ship, safe_directions, size)
        return direction_mapper[direction], 'go home'

    # TODO: よけてしまうのでいまのところ無意味
    # if ship.halite < ATTACK_SHIPYARD_IS_LESS and board.step >= 380:
    #     direction = attack_enemy_shipyard(ship, size, safe_directions, enemy_shipyard_positions)
    #     return direction_mapper[direction]

    direction = attack_heavy_nearest_ship(ship, size, safe_directions, enemy_ship_positions)
    return direction_mapper[direction], 'attack'

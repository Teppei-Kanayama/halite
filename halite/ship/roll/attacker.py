import numpy as np
from kaggle_environments.envs.halite.helpers import *

from halite.ship.strategy import decide_direction_for_shipyard, attack_target_shipyard, attack_heavy_target_ship, \
    attack_heavy_target_ship2
from halite.utils.constants import direction_mapper


def decide_attacker_action(ship, me, board, size: int, safe_directions: List[str],
                           safe_directions_without_shipyards: List[str],
                           responsive_area: List[Tuple[int, int]], step: int, my_position, my_halite,
                           ally_ship_positions, enemy_ship_positions, enemy_ship_ids,
                           ally_shipyard_positions: List[Tuple[int, int]],
                           enemy_shipyard_positions: List[Tuple[int, int]], enemy_shipyard_ids,
                           target_enemy_id, convert_ship_position) -> Tuple[Optional[ShipAction], str]:
    GO_SHIPYARD_WHEN_CARGO_IS_OVER = 300
    ATTACK_SHIPYARD_IS_LESS = 100

    # 「最終ターン」かつ「haliteを500以上積んでいる」ならばconvertする
    if step == 398 and my_halite > 500:
        return ShipAction.CONVERT, 'final_convert'

    # 動ける場所がない場合
    if len(safe_directions) == 0:
        if len(safe_directions_without_shipyards) > 0:
            return direction_mapper[np.random.choice(safe_directions_without_shipyards)], 'kamikaze_attack'
        return np.random.choice(list(direction_mapper.values())), 'random_walk'

    # 「haliteをたくさん載せている」ならshipyardsに帰る
    if my_halite > GO_SHIPYARD_WHEN_CARGO_IS_OVER and len(ally_shipyard_positions) > 0:
        direction = decide_direction_for_shipyard(ally_shipyard_positions, my_position, safe_directions, size)
        return direction_mapper[direction], 'go_home'

    if ship.halite < ATTACK_SHIPYARD_IS_LESS and board.step >= 350:
        direction = attack_target_shipyard(target_enemy_id, ship, size, safe_directions_without_shipyards, enemy_shipyard_positions, enemy_shipyard_ids)
        return direction_mapper[direction], 'attack_shipyard'

    direction = attack_heavy_target_ship2(safe_directions, enemy_ship_positions, my_halite, my_position, enemy_ship_ids, target_enemy_id, size)
    return direction_mapper[direction], 'attack_ship'

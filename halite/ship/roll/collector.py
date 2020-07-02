from kaggle_environments.envs.halite.helpers import *

from halite.ship.ship_utils import calculate_distance
from halite.ship.strategy import decide_direction_for_shipyard, decide_direction_in_responsive_area
from halite.utils.constants import direction_mapper


def decide_collector_action(ship, me, board, size: int, safe_directions: List[Tuple[int, int]], safe_directions_without_shipyards, already_convert: bool,
                            responsive_area: List[Tuple[int, int]], step: int, my_position, my_halite,
                            ally_ship_positions, enemy_ship_positions, ally_shipyard_positions, enemy_shipyard_positions) -> Tuple[Optional[ShipAction], str]:
    MAXIMUM_NUM_OF_SHIPYARDS = 2
    MINE_HALITE_WHEN_HALITE_UNDER_GROUND_IS_OVER = 100
    GO_SHIPYARD_WHEN_CARGO_IS_OVER = 500

    # 「最終ターン」かつ「haliteを500以上積んでいる」ならばconvertする
    if step == 398 and my_halite > 500:
        return ShipAction.CONVERT, 'final_convert'

    # 動ける場所がないならconvertする
    if len(safe_directions) == 0 and my_halite > 500:
        return ShipAction.CONVERT, 'negative_convert'
    if len(safe_directions) == 0:
        return None, 'nothing_to_do'

    # 下記の条件を満たす場合shipyardにconvertする
    # shipyardsが少ない・haliteが十分にある・stayが安全である・まだこのターンにconvertしていない
    # TODO: 一番halieが多いやつがconvertしたほうがお得
    # TODO: オリジナルの関数にしたがうようにする
    if len(ally_shipyard_positions) < min((step // 80 + 1), MAXIMUM_NUM_OF_SHIPYARDS) and me.halite >= 500 and 'stay' in safe_directions and not already_convert:
        return ShipAction.CONVERT, 'positive_convert'

    # その場にhaliteがたくさんあるなら拾う
    if ship.cell.halite > MINE_HALITE_WHEN_HALITE_UNDER_GROUND_IS_OVER and 'stay' in safe_directions:
        return None, 'mine'

    if len(ally_shipyard_positions) > 0:
        # 「序盤でない」かつ「haliteをたくさん載せている」ならshipyardsに帰る
        condition1 = my_halite > GO_SHIPYARD_WHEN_CARGO_IS_OVER and step > 80
        # 「shipyardの近くにいる」かつ「haliteをそこそこ載せている」ならshipyardに帰る
        # TODO: 複数shipyardに対応する
        condition2 = my_halite > 100 and calculate_distance(my_position, ally_shipyard_positions[0], size) <= 5
        if condition1 or condition2:
            direction = decide_direction_for_shipyard(ally_shipyard_positions, my_position, safe_directions, size)
            return direction_mapper[direction], 'go_home'

    # 閾値以上のhaliteがある場所を探す
    direction = decide_direction_in_responsive_area(board, ship, size, safe_directions, responsive_area, halite_threshold=100)
    return direction_mapper[direction], 'discover_halite'

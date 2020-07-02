from kaggle_environments.envs.halite.helpers import *

from halite.ship.ship_utils import calculate_distance
from halite.ship.strategy import decide_direction_for_shipyard, decide_direction_in_responsive_area
from halite.utils.constants import direction_mapper


def decide_collector_action(ship, me, board, size: int, safe_directions: List[Tuple[int, int]], already_convert: bool,
                            responsive_area: List[Tuple[int, int]], enemy_ship_positions):
    MAXIMUM_NUM_OF_SHIPYARDS = 2
    MINE_HALITE_WHEN_HALITE_UNDER_GROUND_IS_OVER = 100
    GO_SHIPYARD_WHEN_CARGO_IS_OVER = 500

    # 「最終ターン」かつ「haliteを500以上積んでいる」ならばconvertする
    if board.step == 398 and ship.halite > 500:
        return ShipAction.CONVERT

    # 動ける場所がないならconvertする
    if len(safe_directions) == 0 and ship.halite > 500:
        return ShipAction.CONVERT
    if len(safe_directions) == 0:
        return None

    # 下記の条件を満たす場合shipyardにconvertする
    # shipyardsが少ない・haliteが十分にある・stayが安全である・まだこのターンにconvertしていない
    # TODO: 一番halieが多いやつがconvertしたほうがお得
    # TODO: オリジナルの関数にしたがうようにする
    if len(me.shipyards) < min((board.step // 80 + 1), MAXIMUM_NUM_OF_SHIPYARDS) and me.halite >= 500 and 'stay' in safe_directions and not already_convert:
        return ShipAction.CONVERT

    # その場にhaliteがたくさんあるなら拾う
    if ship.cell.halite > MINE_HALITE_WHEN_HALITE_UNDER_GROUND_IS_OVER and 'stay' in safe_directions:
        return None

    if len(me.shipyards) > 0:
        # 「序盤でない」かつ「haliteをたくさん載せている」ならshipyardsに帰る
        condition1 = ship.halite > GO_SHIPYARD_WHEN_CARGO_IS_OVER and board.step > 80
        condition2 = ship.halite > 100 and calculate_distance(ship.position, me.shipyards[0].position, size) <= 5
        if condition1 or condition2:
            direction = decide_direction_for_shipyard(me, ship, safe_directions, size)
            return direction_mapper[direction]

    # 閾値以上のhaliteがある場所を探す
    direction = decide_direction_in_responsive_area(board, ship, size, safe_directions, responsive_area, halite_threshold=100)
    if direction:
        return direction_mapper[direction]

    # 閾値以上のhaliteがある場所を探す
    direction = decide_direction_in_responsive_area(board, ship, size, safe_directions, responsive_area, halite_threshold=50)
    if direction:
        return direction_mapper[direction]

    # 閾値以上のhaliteがある場所を探す
    direction = decide_direction_in_responsive_area(board, ship, size, safe_directions, responsive_area, halite_threshold=250)
    if direction:
        return direction_mapper[direction]

    # 閾値以上のhaliteがある場所を探す
    direction = decide_direction_in_responsive_area(board, ship, size, safe_directions, responsive_area, halite_threshold=0)
    if direction:
        return direction_mapper[direction]

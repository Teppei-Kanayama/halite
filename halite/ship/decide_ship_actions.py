from kaggle_environments.envs.halite.helpers import *

from halite.ship.action_manager import ActionManager
from halite.ship.ship_utils import get_nearest_areas
from halite.ship.strategy import decide_direction_for_shipyard, decide_direction_in_responsive_area, attack_heavy_nearest_ship
from halite.utils.constants import direction_mapper, action_to_direction, direction_vector


MAXIMUM_NUM_OF_SHIPYARDS = 2
MINE_HALITE_WHEN_HALITE_UNDER_GROUND_IS_OVER = 100
GO_SHIPYARD_WHEN_CARGO_IS_OVER = 500


# TODO: shipごとにいくつかのstrategyを混ぜていきたい
def decide_one_ship_action(ship, me, board, size: int, safe_directions: List[Tuple[int, int]], already_convert: bool,
                           responsive_area: List[Tuple[int, int]], enemy_ship_positions):
    # 「最終ターン」かつ「haliteを500以上積んでいる」ならばconvertする
    if board.step == 398 and ship.halite > 500:
        return ShipAction.CONVERT

    # 動ける場所がないなら動かない
    # TODO: ランダムに動いた方がいいかもしれない
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

    # 「序盤ではない」かつ「haliteをたくさん載せている」ならshipyardsに帰る
    if ship.halite > GO_SHIPYARD_WHEN_CARGO_IS_OVER and len(me.shipyards) > 0 and board.step > 80:
        direction = decide_direction_for_shipyard(me, ship, safe_directions, size)
        return direction_mapper[direction]

    # 閾値以上のhaliteがある場所を探す
    direction = decide_direction_in_responsive_area(board, ship, size, safe_directions, responsive_area, halite_threshold=100)
    if direction:
        return direction_mapper[direction]

    direction = attack_heavy_nearest_ship(ship, size, safe_directions, enemy_ship_positions)
    return direction_mapper[direction]


def decide_ship_actions(me, board, size):
    actions = {}
    fixed_positions = []
    already_convert = False
    responsive_areas = get_nearest_areas(me.ships, size)
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
        responsive_area = responsive_areas[ship.id]
        action = decide_one_ship_action(ship, me, board, size, safe_directions, already_convert, responsive_area, enemy_ship_positions)
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

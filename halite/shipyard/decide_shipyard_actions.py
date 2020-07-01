import numpy as np
from kaggle_environments.envs.halite.helpers import ShipyardAction


def decide_required_ships(step):
    # TODO: board上のhalite数も見つつ決める（上昇トレンドか下降トレンドか？）
    if step <= 80:
        return 10
    elif step <= 350:
        return 8
    else:
        return 0


def decide_shipyard_actions(me, board, next_ship_positions):
    free_shipyards = [shipyard for shipyard in me.shipyards if shipyard.position not in next_ship_positions]
    if len(me.ships) <= decide_required_ships(board.step) and len(free_shipyards) > 0 and me.halite >= 500:
        target_shipyard = np.random.choice(free_shipyards)
        return {target_shipyard.id: ShipyardAction.SPAWN}
    return {}

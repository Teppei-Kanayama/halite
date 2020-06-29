import numpy as np
from kaggle_environments.envs.halite.helpers import ShipyardAction


def decide_shipyard_actions(me, board, ship_actions):
    # とりあえず数が少なかったらランダムにspawnする
    # TODO: shipが乗っているタイミングではspawnしない
    if len(me.ships) <= 6 and len(me.shipyards) > 0 and me.halite >= 1000:
        target_shipyard = np.random.choice(me.shipyards)
        return {target_shipyard.id: ShipyardAction.SPAWN}
    return {}

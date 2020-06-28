import numpy as np
from kaggle_environments.envs.halite.helpers import ShipyardAction


def decide_shipyard_action(me, board):
    # とりあえず数が少なかったらランダムにspawnする
    if len(me.ships) <= min((board.step // 40), 4) and len(me.shipyards) > 0 and me.halite >= 1000:
        target_shipyard = np.random.choice(me.shipyards)
        return {target_shipyard.id: ShipyardAction.SPAWN}
    return {}

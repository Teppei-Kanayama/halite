import numpy as np
from kaggle_environments.envs.halite.helpers import ShipyardAction


def decide_shipyard_actions(me, board, next_ship_positions):
    # とりあえず数が少なかったらランダムにspawnする
    free_shipyards = [shipyard for shipyard in me.shipyards if shipyard.position not in next_ship_positions]
    if len(me.ships) <= 10 and len(free_shipyards) > 0 and me.halite >= 1000:
        target_shipyard = np.random.choice(free_shipyards)
        return {target_shipyard.id: ShipyardAction.SPAWN}
    return {}

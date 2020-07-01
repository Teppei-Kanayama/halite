import numpy as np
from kaggle_environments.envs.halite.helpers import ShipyardAction


def decide_required_ships(step, percentile):
    if step <= 350:
        return int(min(max((percentile / 5 - 10), 5), 20))
    else:
        return 0


def decide_shipyard_actions(me, board, next_ship_positions):
    free_shipyards = [shipyard for shipyard in me.shipyards if shipyard.position not in next_ship_positions]
    percentile = np.percentile([cell.halite for cell in board.cells.values()], 97)
    required_ships = decide_required_ships(board.step, percentile)
    if len(me.ships) <= required_ships and len(free_shipyards) > 0 and me.halite >= 500:
        target_shipyard = np.random.choice(free_shipyards)
        return {target_shipyard.id: ShipyardAction.SPAWN}
    return {}

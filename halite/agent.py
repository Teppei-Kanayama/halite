from kaggle_environments.envs.halite.helpers import *

from halite.ship.decide_ship_actions import decide_ship_actions
from halite.shipyard.decide_shipyard_actions import decide_shipyard_actions


def agent(obs, config):
    import pdb; pdb.set_trace()

    size = config.size
    board = Board(obs, config)
    me = board.current_player

    ship_actions, next_ship_positions = decide_ship_actions(me, board, size)
    for ship_id, action in ship_actions.items():
        board.ships[ship_id].next_action = action

    shipyard_actions = decide_shipyard_actions(me, board, next_ship_positions)
    for shipyard_id, action in shipyard_actions.items():
        board.shipyards[shipyard_id].next_action = action

    return me.next_actions

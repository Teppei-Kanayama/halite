from kaggle_environments.envs.halite.helpers import *

from halite.ship.decide_ship_actions import decide_ship_action
from halite.shipyard.decide_shipyard_action import decide_shipyard_action


def agent(obs, config):
    size = config.size
    board = Board(obs, config)
    me = board.current_player

    ship_actions = decide_ship_action(me, board, size)
    for ship_id, action in ship_actions.items():
        board.ships[ship_id].next_action = action

    shipyard_actions = decide_shipyard_action(me, board)
    for shipyard_id, action in shipyard_actions.items():
        board.shipyards[shipyard_id].next_action = action

    return me.next_actions

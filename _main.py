from kaggle_environments.envs.halite.helpers import *
import numpy as np
import random


def getDirTo(fromPos, toPos, size):
    fromX, fromY = divmod(fromPos[0],size), divmod(fromPos[1],size)
    toX, toY = divmod(toPos[0],size), divmod(toPos[1],size)
    if fromY < toY: return ShipAction.NORTH
    if fromY > toY: return ShipAction.SOUTH
    if fromX < toX: return ShipAction.EAST
    if fromX > toX: return ShipAction.WEST


# Directions a ship can move
directions = [ShipAction.NORTH, ShipAction.EAST, ShipAction.SOUTH, ShipAction.WEST]


def avoid(my_ship, ships, directions):
    ships.remove(my_ship)
    forbidden_direnctions = [0, 0]
    for s in ships:
        if s[0] == my_ship[0]:
            forbidden_direnctions[0] = 1
        if s[1] == my_ship[1]:
            forbidden_direnctions[1] = 1

    if forbidden_direnctions[0] and forbidden_direnctions[1]:
        directions.pop(0)
        directions.pop(0)
        directions.pop(0)
        directions.pop(0)
    elif forbidden_direnctions[0]:
        directions.pop(3)
        directions.pop(1)
    elif forbidden_direnctions[1]:
        directions.pop(0)
        directions.pop(2)


# Returns the commands we send to our ships and shipyards
def agent(obs, config):
    size = config.size
    board = Board(obs, config)
    me = board.current_player
    ship_states = {}

    # If there are no ships, use first shipyard to spawn a ship.
    if len(me.ships) <= min((board.step // 40), 2) and len(me.shipyards) > 0 and me.halite >= 1000:
        target_shipyard = np.random.choice(me.shipyards)
        target_shipyard.next_action = ShipyardAction.SPAWN

    # If there are no shipyards, convert first ship into shipyard.
    if len(me.shipyards) == 0 and len(me.ships) > 0 and me.halite >= 500:
        me.ships[0].next_action = ShipAction.CONVERT

    for ship in me.ships:
        if ship.next_action is None:

            # Part 1: Set the ship's state
            if ship.halite <= 500:  # If cargo is too low, collect halite
                ship_states[ship.id] = "COLLECT"
            else:  # If cargo gets very big, deposit halite
                ship_states[ship.id] = "DEPOSIT"

            # Part 2: Use the ship's state to select an action
            if ship_states[ship.id] == "COLLECT":
                # If halite at current location running low,
                # move to the adjacent square containing the most halite
                if ship.cell.halite < 100:
                    neighbors = [ship.cell.north.halite, ship.cell.east.halite,
                                 ship.cell.south.halite, ship.cell.west.halite]
                    avoid(ship.position, [v.position for v in board.ships.values()], neighbors)
                    random.shuffle(neighbors)
                    if len(neighbors):
                        best = max(range(len(neighbors)), key=neighbors.__getitem__)
                        ship.next_action = directions[best]
            elif ship_states[ship.id] == "DEPOSIT":
                # Move towards shipyard to deposit cargo
                direction = getDirTo(ship.position, me.shipyards[0].position, size)
                if direction: ship.next_action = direction
            else:
                pass  # no chance

    return me.next_actions

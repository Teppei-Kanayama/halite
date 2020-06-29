from kaggle_environments.envs.halite.helpers import ShipAction

direction_mapper = dict(north=ShipAction.NORTH, east=ShipAction.EAST, south=ShipAction.SOUTH, west=ShipAction.WEST, stay=None)
direction_vector = dict(north=(0, 1), east=(1, 0),  south=(0, -1), west=(-1, 0), stay=(0, 0))


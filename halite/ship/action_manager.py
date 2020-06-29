from typing import Dict, Tuple, List

from kaggle_environments.envs.halite.helpers import ShipAction

from halite.utils.constants import direction_vector


class ActionManager:
    def __init__(self, my_position: Tuple[int, int], my_halite: int, ally_ship_positions: Dict[Tuple[int, int], int],
                 enemy_ship_positions: Dict[Tuple[int, int], int], ally_shipyard_positions: List[Tuple[int, int]],
                 enemy_shipyard_positions: List[Tuple[int, int]], size: int, other_ship_actions: Dict[str, ShipAction]):
        self._my_position = my_position
        self._my_halite = my_halite
        self._ally_ship_positions = ally_ship_positions
        self._enemy_ship_positions = enemy_ship_positions
        self._ally_shipyard_positions = ally_shipyard_positions
        self._enemy_shipyard_positions = enemy_shipyard_positions
        self._size = size
        self._other_ship_actions = other_ship_actions

    def get_action_options(self):
        dangerous_positions = self._get_dangerous_positions(enemy_ship_positions=self._enemy_ship_positions,
                                                            enemy_shipyard_positions=self._enemy_shipyard_positions,
                                                            size=self._size)
        safe_directions = self._get_safe_directions(dangerous_positions=dangerous_positions,
                                                    my_position=self._my_position,
                                                    size=self._size)
        return safe_directions

    @staticmethod
    def _get_dangerous_positions(enemy_ship_positions: Dict[Tuple[int, int], int], enemy_shipyard_positions: List[Tuple[int, int]],
                                 size: int) -> List[Tuple[int, int]]:
        dangerous_positions = []

        # enemy ship
        # TODO: 相手のhaliteが自分よりも多ければ安全
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for pos in enemy_ship_positions.keys():
            dangerous_positions.append(pos)
            for dir in directions:
                dangerous_positions.append(((pos[0] + dir[0]) % size, (pos[1] + dir[1]) % size))

        # my ship
        # TODO: 行動が確定したshipのみ避ける

        # enemy shipyard
        for pos in enemy_shipyard_positions:
            dangerous_positions.append(pos)

        return dangerous_positions

    @staticmethod
    def _get_safe_directions(dangerous_positions: List[Tuple[int, int]], my_position: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        safe_directions = []
        for direction, vector in direction_vector.items():
            target_x = (my_position[0] + vector[0]) % size
            target_y = (my_position[1] + vector[1]) % size
            if (target_x, target_y) not in dangerous_positions:
                safe_directions.append(direction)
        return safe_directions

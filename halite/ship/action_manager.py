from typing import Dict, Tuple, List


from halite.utils.constants import direction_vector


class ActionManager:
    def __init__(self, my_position: Tuple[int, int], my_halite: int, ally_ship_positions: Dict[Tuple[int, int], int],
                 enemy_ship_positions: Dict[Tuple[int, int], int], ally_shipyard_positions: List[Tuple[int, int]],
                 enemy_shipyard_positions: List[Tuple[int, int]], size: int, fixed_positions: List[Tuple[int, int]]):
        self._my_position = my_position
        self._my_halite = my_halite
        self._ally_ship_positions = ally_ship_positions
        self._enemy_ship_positions = enemy_ship_positions
        self._ally_shipyard_positions = ally_shipyard_positions
        self._enemy_shipyard_positions = enemy_shipyard_positions
        self._size = size
        self._fixed_positions = fixed_positions

    def get_action_options(self, avoid_shipyards: bool) -> List[str]:
        dangerous_positions = self._get_dangerous_positions(enemy_ship_positions=self._enemy_ship_positions,
                                                            enemy_shipyard_positions=self._enemy_shipyard_positions,
                                                            fixed_positions=self._fixed_positions,
                                                            my_halite = self._my_halite,
                                                            size=self._size,
                                                            avoid_shipyards=avoid_shipyards)
        safe_directions = self._get_safe_directions(dangerous_positions=dangerous_positions,
                                                    my_position=self._my_position,
                                                    size=self._size)
        return safe_directions

    @staticmethod
    def _get_dangerous_positions(enemy_ship_positions: Dict[Tuple[int, int], int], enemy_shipyard_positions: List[Tuple[int, int]],
                                 fixed_positions: List[Tuple[int, int]], my_halite: int, size: int,
                                 avoid_shipyards: bool) -> List[Tuple[int, int]]:
        dangerous_positions = []

        # enemy ship
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        lighter_enemy_ship_positions = {k: v for k, v in enemy_ship_positions.items() if v <= my_halite}
        for pos in lighter_enemy_ship_positions.keys():
            dangerous_positions.append(pos)
            for dir in directions:
                dangerous_positions.append(((pos[0] + dir[0]) % size, (pos[1] + dir[1]) % size))

        # my ship
        dangerous_positions += fixed_positions

        # enemy shipyard
        if avoid_shipyards:
            for pos in enemy_shipyard_positions:
                dangerous_positions.append(pos)

        return dangerous_positions

    @staticmethod
    def _get_safe_directions(dangerous_positions: List[Tuple[int, int]], my_position: Tuple[int, int], size: int) -> List[str]:
        safe_directions = []
        for direction, vector in direction_vector.items():
            target_x = (my_position[0] + vector[0]) % size
            target_y = (my_position[1] + vector[1]) % size
            if (target_x, target_y) not in dangerous_positions:
                safe_directions.append(direction)
        return safe_directions

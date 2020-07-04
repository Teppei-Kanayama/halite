from abc import abstractmethod
from typing import List, Tuple, Dict


class RollTemplate:

    def __init__(self, safe_directions: List[str],  safe_directions_without_shipyards: List[str],
                 responsive_area: List[Tuple[int, int]], step: int, my_position: Tuple[int, int], my_halite: int,
                 ally_ship_halites: Dict[Tuple[int, int], int], enemy_ship_halites: Dict[Tuple[int, int], int],
                 ally_ship_ids: Dict[Tuple[int, int], str], enemy_ship_ids: Dict[Tuple[int, int], str],
                 ally_shipyard_ids: Dict[Tuple[int, int], str], enemy_shipyard_ids: Dict[Tuple[int, int], str],
                 target_enemy_id: str, convert_ship_position: Tuple[int, int], halite_under: int, size: int) -> None:
        self._safe_directions = safe_directions
        self._safe_directions_without_shipyards = safe_directions_without_shipyards
        self._responsive_area = responsive_area
        self._step = step
        self._my_position = my_position
        self._my_halite = my_halite
        self._ally_ship_halites = ally_ship_halites
        self._enemy_ship_halites = enemy_ship_halites
        self._ally_ship_ids = ally_ship_ids
        self._enemy_ship_ids = enemy_ship_ids
        self._ally_shipyard_ids = ally_shipyard_ids
        self._enemy_shipyard_ids = enemy_shipyard_ids
        self._target_enemy_id = target_enemy_id
        self._convert_ship_position = convert_ship_position
        self._halite_under = halite_under  # ship.cell.halite
        self._size = size

    @abstractmethod
    def decide_next_action(self):
        raise NotImplementedError

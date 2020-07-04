import numpy as np
from kaggle_environments.envs.halite.helpers import *

from halite.ship.roll.roll_template import RollTemplate
from halite.ship.strategy import decide_direction_toward_multiple_position_options, attack_target_shipyard
from halite.ship.strategy import attack_heavy_target_ship, attack_heavy_target_ship2
from halite.utils.constants import direction_mapper
from halite.utils.strategy_constants import *


class Attacker(RollTemplate):

    def decide_next_action(self):
        # 「最終ターン」かつ「haliteを500以上積んでいる」ならばconvertする
        if self._step == 398 and self._my_halite > 500:
            return ShipAction.CONVERT, 'final_convert'

        # 動ける場所がない場合
        if len(self._safe_directions) == 0:
            if len(self._safe_directions_without_shipyards) > 0:
                return direction_mapper[np.random.choice(self._safe_directions_without_shipyards)], 'kamikaze_attack'
            return np.random.choice(list(direction_mapper.values())), 'random_walk'

        # 「haliteをたくさん載せている」ならshipyardsに帰る
        if self._my_halite > ATTACKER_GO_SHIPYARD_WHEN_CARGO_IS_OVER and len(self._ally_shipyard_ids) > 0:
            direction = decide_direction_toward_multiple_position_options(destination_chioice=list(self._ally_shipyard_ids.keys()), my_position=self._my_position,
                                                                          safe_directions=self._safe_directions, size=self._size)
            return direction_mapper[direction], 'go_home'

        if self._my_halite < ATTACKER_ATTACK_SHIPYARD_IS_LESS and self._step >= ATTACKER_START_SHIPYARD_ATTACK:
            direction = attack_target_shipyard(target_enemy_id=self._target_enemy_id, my_position=self._my_position, size=self._size,
                                               safe_directions_without_shipyards=self._safe_directions_without_shipyards,
                                               enemy_shipyard_ids=self._enemy_shipyard_ids)
            if direction:
                return direction_mapper[direction], 'attack_shipyard'

        direction = attack_heavy_target_ship(safe_directions=self._safe_directions, enemy_ship_halites=self._enemy_ship_halites,
                                              my_halite=self._my_halite, my_position=self._my_position, enemy_ship_ids=self._enemy_ship_ids,
                                              target_enemy_id=self._target_enemy_id, size=self._size)
        return direction_mapper[direction], 'attack_ship'

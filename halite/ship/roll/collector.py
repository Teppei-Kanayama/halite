from kaggle_environments.envs.halite.helpers import *

from halite.ship.roll.roll_template import RollTemplate
from halite.ship.ship_utils import calculate_distance
from halite.ship.strategy import decide_direction_for_shipyard, decide_direction_in_responsive_area
from halite.utils.constants import direction_mapper


class Controller(RollTemplate):

    def decide_next_action(self):
        MAXIMUM_NUM_OF_SHIPYARDS = 2
        MINE_HALITE_WHEN_HALITE_UNDER_GROUND_IS_OVER = 100
        GO_SHIPYARD_WHEN_CARGO_IS_OVER = 500

        # 「最終ターン」かつ「haliteを500以上積んでいる」ならばconvertする
        if self._step == 398 and self._my_halite > 500:
            return ShipAction.CONVERT, 'final_convert'

        # 動ける場所がないならconvertする
        if len(self._safe_directions) == 0 and self._my_halite > 500:
            return ShipAction.CONVERT, 'negative_convert'
        if len(self._safe_directions) == 0:
            return None, 'nothing_to_do'

        condition1 = len(self._ally_shipyard_ids) < min(self._get_required_shipyards(self._step), MAXIMUM_NUM_OF_SHIPYARDS)
        condition2 = self._my_halite >= 500
        condition3 = 'stay' in self._safe_directions
        condition4 = self._my_position not in self._ally_shipyard_ids.keys()
        condition5 = (self._convert_ship_position is None) or (self._my_position == self._convert_ship_position)
        if condition1 and condition2 and condition3 and condition4 and condition5:
            return ShipAction.CONVERT, 'positive_convert'

        # その場にhaliteがたくさんあるなら拾う
        if self._halite_under > MINE_HALITE_WHEN_HALITE_UNDER_GROUND_IS_OVER and 'stay' in self._safe_directions:
            return None, 'mine'

        if len(self._ally_shipyard_ids) > 0:
            # 「序盤でない」かつ「haliteをたくさん載せている」ならshipyardsに帰る
            condition1 = self._my_halite > GO_SHIPYARD_WHEN_CARGO_IS_OVER and self._step > 80
            # 「shipyardの近くにいる」かつ「haliteをそこそこ載せている」ならshipyardに帰る
            # TODO: 複数shipyardに対応する
            condition2 = self._my_halite > 100 and calculate_distance(self._my_position, list(self._ally_shipyard_ids.keys())[0], self._size) <= 5
            if condition1 or condition2:
                direction = decide_direction_for_shipyard(list(self._ally_shipyard_ids.keys()), self._my_position, self._safe_directions, self._size)
                return direction_mapper[direction], 'go_home'

        # 閾値以上のhaliteがある場所を探す
        # TODO: boardはあまり使いたくないが・・・
        direction = decide_direction_in_responsive_area(board=self._board, my_position=self._my_position, size=self._size, safe_directions=self._safe_directions,
                                                        responsive_area=self._responsive_area, halite_thresholds=[100, 50, 25, 5, 0])
        return direction_mapper[direction], 'discover_halite'

    @staticmethod
    def _get_required_shipyards(step: int) -> int:
        if step < 80:
            return 1
        if step < 300:
            return 2
        return 1

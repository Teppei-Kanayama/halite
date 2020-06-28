import unittest

from halite.ship.action_manager import ActionManager


class TestActionManager(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_get_dangerous_positions(self):
        ship_positions = [(5, 15), (15, 15), (5, 5), (15, 5)]
        shipyard_positions = []
        my_position = (5, 15)
        actual = ActionManager._get_dangerous_positions(ship_positions, shipyard_positions, my_position)
        expected = [(15, 15), (16, 15), (14, 15), (15, 16), (15, 14), (5, 5), (6, 5), (4, 5), (5, 6), (5, 4),
                    (15, 5), (16, 5), (14, 5), (15, 6), (15, 4)]
        self.assertEqual(actual, expected)

    def test_get_safe_directions(self):
        dangerous_positions = [(5, 15), (6, 15), (14, 15)]
        my_position = (5, 15)
        actual = ActionManager._get_safe_directions(dangerous_positions, my_position)
        expected = ['north', 'south', 'west']
        self.assertEqual(actual, expected)

import pytest
import warnings
from quacks import Player, Board, Bag, Ingredient


class TestSimulateRound:
    def test_token_beyond_last_space(self):
        """Check that the token can't be placed past the final space on the board - i.e. the final money/points
        space will always be left uncovered."""
        player = Player()

        # give the player no white tokens and lots of ones with high values, so they will definitely reach the end
        player.bag.ingredients['master'] = [Ingredient('blue', 4) for i in range(1, 50)]

        test_round = player.simulate_round()
        assert test_round['final_position'] == player.board.last_playable_space

    def test_stop_picking_when_empty(self):
        """Check that no more tokens will be picked when the bag is empty."""
        player = Player()
        player.bag.ingredients['master'] = [Ingredient('white', 1), Ingredient('white', 2)]
        assert player.simulate_round()['final_position'] == 3

    def test_stop_picking_when_exploded(self):
        """Check that no more tokens will be picked when the explosion limit is exceeded."""
        player = Player()
        player.bag.ingredients['master'] = [Ingredient('white', 1) for i in range(1, 20)]
        assert player.simulate_round()['final_position'] == 8

    @pytest.mark.parametrize('risk_tolerance, expected_position', [(0.49, 0), (0.5, 10), (0.51, 10)])
    def test_stop_picking_when_risk_exceeded(self, risk_tolerance, expected_position):
        """Check that no more are picked when the chance to explode is higher than the risk."""
        player = Player()
        player.bag.ingredients['master'] = [Ingredient('white', 10), Ingredient('blue', 10)]
        test_round = player.simulate_round(stop_before_explosion=True, risk_tolerance=risk_tolerance)
        assert test_round['final_position'] == expected_position

    @pytest.mark.parametrize('droplet_position, rat_tails, expected_position', [(2, 0, 6), (0, 2, 6), (2, 2, 8)])
    def test_droplet_and_rat_tails_added(self, droplet_position, rat_tails, expected_position):
        """Check that the droplet position and rat tails are reflected in the final position correctly."""
        player = Player()
        player.droplet_position = droplet_position
        player.rat_tails = rat_tails
        player.bag.ingredients['master'] = [Ingredient('blue', 2), Ingredient('blue', 2)]
        assert player.simulate_round()['final_position'] == expected_position

    def test_reset_ingredients(self):
        """Check that the starting and ending current ingredients are the same as the master ones."""
        player = Player()
        player.bag.ingredients['master'] = [Ingredient('blue', 2)]
        player.bag.ingredients['current'] = []

        test_round = player.simulate_round()

        current_ingredients = [(ingredient.value, ingredient.color) for ingredient in player.bag.ingredients['current']]
        master_ingredients = [(ingredient.value, ingredient.color) for ingredient in player.bag.ingredients['master']]

        # checking that the master ingredients are correctly being used for picking and that the current and
        # master ingredients match at the end.
        assert test_round['final_position'] == 2 and current_ingredients == master_ingredients

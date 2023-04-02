import pytest
from quacks import Bag, Ingredient


class TestSumCurrentIngredientColor:
    def test_default_sum(self):
        """Check that the sum of all the white ingredients in a starting bag is 11."""
        assert Bag().sum_ingredient_color('white') == 11

    def test_empty_color(self):
        """Check that if a no ingredients of a selected color exist in the bag, the sum is 0."""
        assert Bag().sum_ingredient_color('made_up_color') == 0

    def test_no_color_passed(self):
        """Error when no parameter is passed."""
        with pytest.raises(TypeError):
            Bag().sum_ingredient_color()


class TestMaxCurrentIngredientColor:
    def test_default_max(self):
        """Check the max ingredient value in the starting bag is a (white) 3."""
        assert Bag().max_ingredient_color('white') == 3

    def test_empty_color(self):
        """Return 0 when looking for the max of a color that doesn't exist in the bag."""
        assert Bag().max_ingredient_color('made_up_color') == 0

    def test_no_color_passed(self):
        """Error when no parameter is passed."""
        with pytest.raises(TypeError):
            Bag().max_ingredient_color()

    def test_empty_list(self):
        """Return 0 when the list is empty"""
        bag = Bag()
        bag.ingredients['current'] = []
        assert bag.max_ingredient_color('white') == 0


class TestPickedWhiteValue:
    def test_empty_value(self):
        """Check value is 0 when the picked list is empty"""
        assert Bag().current_picked_white_value() == 0

    def test_all_default_picked(self):
        """Check value is 11 when all the default white tokens have been picked"""
        bag = Bag()
        bag.ingredients['picked'] = bag.ingredients['master']
        assert bag.current_picked_white_value() == 11


class TestChanceToExplode:
    def test_empty_current_ingredients(self):
        """Check that we're not trying to divide by 0"""
        bag = Bag()
        bag.current_ingredients = []
        assert bag.chance_to_explode() == 0

    def test_default_chance(self):
        """Check that with no tokens picked, the chance to explode should be 0"""
        assert Bag().chance_to_explode() == 0

    def test_one_needed_to_explode(self):
        """Check that the chance is correct when only 1 is needed to explode"""
        bag = Bag()
        bag.ingredients['picked'] = [
            Ingredient('white', 3), Ingredient('white', 2), Ingredient('white', 1), Ingredient('white', 1)
        ]
        bag.ingredients['current'] = [
            Ingredient('white', 2), Ingredient('white', 1), Ingredient('white', 1),
            Ingredient('orange', 1), Ingredient('green', 1)
        ]
        assert bag.chance_to_explode() == 3/5

    def test_two_needed_to_explode(self):
        """Check that only the 2 or 3 value tokens will count towards the probability when 2 more needed to explode"""
        bag = Bag()
        bag.ingredients['picked'] = [
            Ingredient('white', 2), Ingredient('white', 1), Ingredient('white', 1), Ingredient('white', 1),
            Ingredient('white', 1)
        ]
        bag.ingredients['current'] = [
            Ingredient('white', 3), Ingredient('white', 2), Ingredient('orange', 1), Ingredient('green', 1)
        ]
        assert bag.chance_to_explode() == 2 / 4

    def test_three_needed_to_explode(self):
        """Check that only the 3 value token will count towards the probability when 3 more needed to explode"""
        bag = Bag()
        bag.ingredients['picked'] = [
            Ingredient('white', 2), Ingredient('white', 2), Ingredient('white', 1)
        ]
        bag.ingredients['current'] = [
            Ingredient('white', 3), Ingredient('white', 1), Ingredient('white', 1), Ingredient('white', 1),
            Ingredient('orange', 1), Ingredient('green', 1)
        ]
        assert bag.chance_to_explode() == 1 / 6


class TestPickIngredient:
    def test_pick_from_empty_bag(self):
        """Check that None is returned when picking from an empty bag"""
        bag = Bag()
        bag.ingredients['current'] = []
        assert bag.pick_ingredient() is None


class TestResetPickedIngredients:
    def test_current_equals_master(self):
        """Check that the current_ingredients list is now the same as the master_ingredients"""
        bag = Bag()
        bag.pick_ingredient()
        bag.reset_picked_ingredients()
        assert (
            len(bag.ingredients['current']) == len(bag.ingredients['master'])
        )

class TestAddIngredient:
    def test_add_white_one_token(self):
        """Check that when adding a white token with value 1, the correct object is returned and the length of
        master_ingredients is 1 more than before."""
        bag = Bag()
        before_ingredient_count = len(bag.ingredients['master'])
        added_token = bag.add_ingredient('white', 1)
        after_ingredient_count = len(bag.ingredients['master'])
        assert (
            added_token.color == 'white'
            and added_token.value == 1
            and before_ingredient_count == after_ingredient_count - 1
        )

    def test_no_parameters_passed(self):
        """Error when no parameter is passed."""
        with pytest.raises(TypeError):
            assert Bag().add_ingredient()


class TestRemoveIngredient:
    def test_remove_a_white_one_token(self):
        """Check that when removing a white token with value 1, the correct object is returned and the length of
        master_ingredients is 1 less than before."""
        bag = Bag()
        before_ingredient_count = len(bag.ingredients['master'])
        removed_token = bag.remove_ingredient('white', 1)
        after_ingredient_count = len(bag.ingredients['master'])
        assert (
            removed_token.color == 'white'
            and removed_token.value == 1
            and before_ingredient_count == after_ingredient_count + 1
        )

    def test_remove_from_empty_color(self):
        """Check that when trying to remove an ingredient by a color that doesn't exist, that None is returned
        and the length of master_ingredients is the same as before."""
        bag = Bag()
        before_ingredient_count = len(bag.ingredients['master'])
        removed_token = bag.remove_ingredient('made_up_color', 1)
        after_ingredient_count = len(bag.ingredients['master'])
        assert removed_token is None and before_ingredient_count == after_ingredient_count

    def test_remove_wrong_value(self):
        """Check that when trying to remove an ingredient by a value that doesn't exist, that None is returned
        and the length of master_ingredients is the same as before."""
        bag = Bag()
        before_ingredient_count = len(bag.ingredients['master'])
        removed_token = bag.remove_ingredient('white', 10)
        after_ingredient_count = len(bag.ingredients['master'])
        assert removed_token is None and before_ingredient_count == after_ingredient_count

    def test_remove_from_empty_bag(self):
        """Check that trying to remove an ingredient from an empty bag will return nothing and that the
        master_ingredients list is still empty."""
        bag = Bag()
        bag.ingredients['master'] = []
        removed_ingredient = bag.remove_ingredient('white', 1)
        assert removed_ingredient is None and len(bag.ingredients['master']) == 0

    def test_no_parameters_passed(self):
        """Error when no parameter is passed."""
        with pytest.raises(TypeError):
            assert Bag().remove_ingredient()
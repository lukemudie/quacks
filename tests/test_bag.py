import pytest
from quacks import Bag


class TestSumCurrentIngredientColor:
    def test_default_sum(self):
        """Check that the sum of all the white ingredients in a starting bag is 11."""
        assert Bag().sum_current_ingredient_color('white') == 11

    def test_empty_color(self):
        """Check that if a no ingredients of a selected color exist in the bag, the sum is 0."""
        assert Bag().sum_current_ingredient_color('made_up_color') == 0

    def test_no_color_passed(self):
        """Error when no parameter is passed."""
        with pytest.raises(TypeError):
            Bag().sum_current_ingredient_color()


class TestMaxCurrentIngredientColor:
    def test_default_max(self):
        """Check the max ingredient value in the starting bag is a (white) 3."""
        assert Bag().max_current_ingredient_color('white') == 3

    def test_empty_color(self):
        """Error when looking for the max of a color that doesn't exist in the bag."""
        with pytest.raises(ValueError):
            Bag().max_current_ingredient_color('made_up_color')

    def test_no_color_passed(self):
        """Error when no parameter is passed."""
        with pytest.raises(TypeError):
            Bag().max_current_ingredient_color()


class TestPickIngredient:
    def test_pick_from_empty_bag(self):
        """Check that None is returned when picking from an empty bag"""
        bag = Bag()
        bag.current_ingredients = []
        assert bag.pick_ingredient() is None


class TestAddIngredient:
    def test_add_white_one_token(self):
        """Check that when adding a white token with value 1, the correct object is returned and the length of
        master_ingredients is 1 more than before."""
        bag = Bag()
        before_ingredient_count = len(bag.master_ingredients)
        added_token = bag.add_ingredient('white', 1)
        after_ingredient_count = len(bag.master_ingredients)
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
        before_ingredient_count = len(bag.master_ingredients)
        removed_token = bag.remove_ingredient('white', 1)
        after_ingredient_count = len(bag.master_ingredients)
        assert (
            removed_token.color == 'white'
            and removed_token.value == 1
            and before_ingredient_count == after_ingredient_count + 1
        )

    def test_remove_from_empty_color(self):
        """Check that when trying to remove an ingredient by a color that doesn't exist, that None is returned
        and the length of master_ingredients is the same as before."""
        bag = Bag()
        before_ingredient_count = len(bag.master_ingredients)
        removed_token = bag.remove_ingredient('made_up_color', 1)
        after_ingredient_count = len(bag.master_ingredients)
        assert removed_token is None and before_ingredient_count == after_ingredient_count

    def test_remove_wrong_value(self):
        """Check that when trying to remove an ingredient by a value that doesn't exist, that None is returned
        and the length of master_ingredients is the same as before."""
        bag = Bag()
        before_ingredient_count = len(bag.master_ingredients)
        removed_token = bag.remove_ingredient('white', 10)
        after_ingredient_count = len(bag.master_ingredients)
        assert removed_token is None and before_ingredient_count == after_ingredient_count

    def test_remove_from_empty_bag(self):
        """Check that trying to remove an ingredient from an empty bag will return nothing and that the
        master_ingredients list is still empty."""
        bag = Bag()
        bag.master_ingredients = []
        removed_ingredient = bag.remove_ingredient('white', 1)
        assert removed_ingredient is None and len(bag.master_ingredients) == 0

    def test_no_parameters_passed(self):
        """Error when no parameter is passed."""
        with pytest.raises(TypeError):
            assert Bag().remove_ingredient()
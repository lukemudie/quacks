import pytest
from quacks import Bag


class TestSumCurrentIngredientColor:
    def test_default_sum(self):
        assert Bag().sum_current_ingredient_color('white') == 11

    def test_empty_color(self):
        assert Bag().sum_current_ingredient_color('made_up_color') == 0

    def test_no_color_passed(self):
        with pytest.raises(TypeError):
            Bag().sum_current_ingredient_color()


class TestMaxCurrentIngredientColor:
    def test_default_max(self):
        assert Bag().max_current_ingredient_color('white') == 3

    def test_empty_color(self):
        with pytest.raises(ValueError):
            Bag().max_current_ingredient_color('made_up_color')

    def test_no_color_passed(self):
        with pytest.raises(TypeError):
            Bag().max_current_ingredient_color()


class TestPickIngredient:
    def test_pick_from_empty_bag(self):
        bag = Bag()
        bag.current_ingredients = []
        assert bag.pick_ingredient() is None


class TestAddIngredient:
    def test_add_white_one_token(self):
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
        with pytest.raises(TypeError):
            assert Bag().add_ingredient()


class TestRemoveIngredient:
    def test_remove_a_white_one_token(self):
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
        assert Bag().remove_ingredient('made_up_color', 1) is None

    def test_remove_wrong_value(self):
        assert Bag().remove_ingredient('white', 10) is None

    def test_remove_from_empty_bag(self):
        bag = Bag()
        bag.master_ingredients = []
        assert bag.remove_ingredient('white', 1) is None

    def test_no_parameters_passed(self):
        with pytest.raises(TypeError):
            assert Bag().remove_ingredient()
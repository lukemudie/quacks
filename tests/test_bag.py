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

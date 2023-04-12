import pytest
import warnings
from quacks import Bag, Ingredient


class TestSumIngredientColor:
    @pytest.mark.parametrize('test_input, expected_output', [('master', 11), ('current', 4), ('picked', 6)])
    def test_specified_set(self, test_input, expected_output):
        """Check that passing the set_of_ingredients parameter causes the sum to take place on the correct set."""
        bag = Bag()
        bag.ingredients['current'] = [Ingredient('white', 2), Ingredient('white', 1), Ingredient('white', 1)]
        bag.ingredients['picked'] = [Ingredient('white', 3), Ingredient('white', 2), Ingredient('white', 1)]
        assert bag.sum_ingredient_color('white', test_input) == expected_output

    def test_no_set_specified(self):
        """Check that not giving a set_of_ingredients will still return the correct result."""
        assert Bag().sum_ingredient_color('white') == 11

    def test_empty_color(self):
        """Check that if a no ingredients of a selected color exist in the bag, the sum is 0."""
        assert Bag().sum_ingredient_color('made_up_color') == 0

    def test_wrong_set_name_warning(self):
        """Check that if the set of ingredients parameter is wrong, the sum is 0 and a warning is raised."""
        with pytest.warns(UserWarning):
            assert Bag().sum_ingredient_color('white', 'made_up_set') == 0
            warnings.warn("There is no set of ingredients 'made_up_set', so the sum will be 0.", UserWarning)

    def test_no_color_passed(self):
        """Error when no parameter is passed."""
        with pytest.raises(TypeError):
            Bag().sum_ingredient_color()

    def test_empty_list(self):
        """Return 0 when the list is empty."""
        bag = Bag()
        bag.ingredients['current'] = []
        assert bag.sum_ingredient_color('white') == 0


class TestMaxIngredientColor:
    @pytest.mark.parametrize('test_input, expected_output', [('master', 3), ('current', 2), ('picked', 1)])
    def test_specified_set(self, test_input, expected_output):
        """Check that passing the set_of_ingredients parameter causes the sum to take place on the correct set."""
        bag = Bag()
        bag.ingredients['current'] = [Ingredient('white', 2), Ingredient('white', 1), Ingredient('white', 1)]
        bag.ingredients['picked'] = [Ingredient('white', 1), Ingredient('white', 1), Ingredient('white', 1)]
        assert bag.max_ingredient_color('white', test_input) == expected_output

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

    def test_wrong_set_name_warning(self):
        """Check that if the set of ingredients parameter is wrong, the sum is 0 and a warning is raised."""
        with pytest.warns(UserWarning):
            assert Bag().max_ingredient_color('white', 'made_up_set') == 0
            warnings.warn("There is no set of ingredients 'made_up_set', so the max will be 0.", UserWarning)

    def test_empty_list(self):
        """Return 0 when the list is empty."""
        bag = Bag()
        bag.ingredients['current'] = []
        assert bag.max_ingredient_color('white') == 0


class TestPickedWhiteValue:
    def test_empty_value(self):
        """Check value is 0 when the picked list is empty."""
        assert Bag().get_picked_white_value() == 0

    def test_all_default_picked(self):
        """Check value is 11 when all the default white tokens have been picked."""
        bag = Bag()
        bag.ingredients['picked'] = bag.ingredients['master']
        assert bag.get_picked_white_value() == 11


class TestChanceToExplode:
    def test_empty_current_ingredients(self):
        """Check that we're not trying to divide by 0."""
        bag = Bag()
        bag.current_ingredients = []
        assert bag.chance_to_explode() == 0

    def test_default_chance(self):
        """Check that with no tokens picked, the chance to explode should be 0."""
        assert Bag().chance_to_explode() == 0

    def test_one_needed_to_explode(self):
        """Check that the chance is correct when only 1 is needed to explode."""
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
        """Check that only the 2 or 3 value tokens will count towards the probability when 2 more needed to explode."""
        bag = Bag()
        bag.ingredients['picked'] = [
            Ingredient('white', 2), Ingredient('white', 1), Ingredient('white', 1), Ingredient('white', 1),
            Ingredient('white', 1)
        ]
        bag.ingredients['current'] = [
            Ingredient('white', 3), Ingredient('white', 2), Ingredient('orange', 1), Ingredient('green', 1)
        ]
        assert bag.chance_to_explode() == 2/4

    def test_three_needed_to_explode(self):
        """Check that only the 3 value token will count towards the probability when 3 more needed to explode."""
        bag = Bag()
        bag.ingredients['picked'] = [
            Ingredient('white', 2), Ingredient('white', 2), Ingredient('white', 1)
        ]
        bag.ingredients['current'] = [
            Ingredient('white', 3), Ingredient('white', 1), Ingredient('white', 1), Ingredient('white', 1),
            Ingredient('orange', 1), Ingredient('green', 1)
        ]
        assert bag.chance_to_explode() == 1/6


class TestPickIngredient:
    def test_pick_from_empty_bag(self):
        """Check that None is returned when picking from an empty bag."""
        bag = Bag()
        bag.ingredients['current'] = []
        assert bag.pick_ingredient() is None

    def test_pick_one_ingredient(self):
        """Check that the correct ingredient is picked from a bag with one Ingredient."""
        bag = Bag()
        bag.ingredients['current'] = [Ingredient('white', 1)]
        picked_ingredient = bag.pick_ingredient()
        assert picked_ingredient.color == 'white' and picked_ingredient.value == 1


class TestResetPickedIngredients:
    def test_current_equals_master(self):
        """Check that the current_ingredients list is the same as the master_ingredients after resetting."""
        bag = Bag()
        bag.pick_ingredient()
        bag.reset_picked_ingredients()
        current_ingredients = [(ingredient.value, ingredient.color) for ingredient in bag.ingredients['current']]
        master_ingredients = [(ingredient.value, ingredient.color) for ingredient in bag.ingredients['master']]
        assert current_ingredients == master_ingredients


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

    @pytest.mark.parametrize(
        'test_color, test_value, expected_output',
        [('made_up_color', 1, None), ('white', 10, None), ('made_up_color', 10, None)]
    )
    def test_wrong_parameters(self, test_color, test_value, expected_output):
        """Check that if incorrect parameters are given, None is returned and an appropriate warning is given."""
        with pytest.warns(UserWarning):
            bag = Bag()
            before_ingredient_count = len(bag.ingredients['master'])
            removed_token = bag.remove_ingredient(test_color, test_value)
            after_ingredient_count = len(bag.ingredients['master'])
            assert removed_token is expected_output and before_ingredient_count == after_ingredient_count
            warnings.warn(f"There is no ingredient in the bag that matches ({test_color}, {test_value}), "
                          f"so none have been removed!", UserWarning)

    def test_remove_from_empty_bag(self):
        """Check that trying to remove an ingredient from an empty bag will return nothing and that the
        master_ingredients list is still empty."""
        with pytest.warns(UserWarning):
            bag = Bag()
            bag.ingredients['master'] = []
            removed_ingredient = bag.remove_ingredient('white', 1)
            assert removed_ingredient is None and len(bag.ingredients['master']) == 0
            warnings.warn(f"There is no ingredient in the bag that matches (white, 1), "
                          f"so none have been removed!", UserWarning)

    def test_no_parameters_passed(self):
        """Error when no parameter is passed."""
        with pytest.raises(TypeError):
            assert Bag().remove_ingredient()


class TestReturnToBaseline:
    def test_master_ingredients_reset(self):
        """Check that the ingredients in the master list are as they should be."""
        bag = Bag()
        original_master_list = [(ingredient.value, ingredient.color) for ingredient in bag.ingredients['master']]
        bag.add_ingredient('purple', 1)
        bag.remove_ingredient('white', 1)
        modified_master_list = [(ingredient.value, ingredient.color) for ingredient in bag.ingredients['master']]
        bag.return_to_baseline()
        returned_master_list = [(ingredient.value, ingredient.color) for ingredient in bag.ingredients['master']]
        assert original_master_list == returned_master_list and returned_master_list != modified_master_list

import pandas as pd
import numpy as np
import random
from copy import deepcopy
import matplotlib.pyplot as plt
import seaborn as sns


class Ingredient:
    """
    A class used to represent a single ingredient token.

    Attributes
    ----------
    color : str
        The color of the ingredient. Determines the effect activated when picked.
    value : int
        The value on the ingredient token; Determines how many spaces it will advance when picked.
    """
    def __init__(self, color, value):
        self.color = color
        self.value = value


class Bag:
    """
    A class used to represent a bag of ingredients in the game Quacks of Quedlinburg.

    Attributes
    ----------
    ingredients : dict of lists of the Ingredient class
        'master': all ingredients available to the player.
        'current': the ingredients currently in the bag that have not been picked.
        'picked': the ingredients that have been picked and are no longer in the bag.
    explosion_limit : int
        The total value of white ingredients that have to be exceeded when pulled in order
        for the player to explode.
    """

    def __init__(self):
        """Initialise the bag with the standard starting ingredients."""
        self.ingredients = {'master': [], 'current': [], 'picked': []}
        self.return_to_baseline()
        self.ingredients['current'] = deepcopy(self.ingredients['master'])
        self.ingredients['picked'] = []
        self.explosion_limit = 7

    def print_ingredients(self, set_of_ingredients='master'):
        """
        Prints out a list of all the ingredient values in the bag, grouped by color.

        Parameters
        ----------
        set_of_ingredients : str
            'master' to show all ingredients that have been added to the bag or 'current' to show
            all that are currently in the bag during a round in case some have been picked out already

        Returns
        -------
        None
        """
        if set_of_ingredients in ['master', 'current', 'picked']:
            ingredients = self.ingredients[set_of_ingredients]
            print(f"Showing the '{set_of_ingredients}' set of ingredients:")

            unique_colors = list(dict.fromkeys([ingredient.color for ingredient in ingredients]))
            for color in unique_colors:
                print(f'    {color}: ', end='')
                print([ingredient.value for ingredient in ingredients if ingredient.color == color])
        else:
            print(f"The '{set_of_ingredients}' set of ingredients does not exist.")

    def sum_current_ingredient_color(self, color):
        """Adds up the values of all the tokens of a given color that are in the current ingredients"""
        return sum([ingredient.value for ingredient in self.ingredients['current'] if ingredient.color == color])

    def max_current_ingredient_color(self, color):
        """Find the max from the values of all the tokens of a given color that are in the current ingredients"""
        if len(self.ingredients['current']) == 0 \
                or color not in list(dict.fromkeys([ingredient.color for ingredient in self.ingredients['current']])):
            return 0
        else:
            return max([ingredient.value for ingredient in self.ingredients['current'] if ingredient.color == color])

    def current_picked_white_value(self):
        """Gives the total of all the white ingredients that have been picked so far"""
        return sum([ingredient.value for ingredient in self.ingredients['picked'] if ingredient.color == 'white'])

    def chance_to_explode(self):
        """Get the probability of exploding on the next pick based on what has been picked so far"""
        value_needed_to_explode = self.explosion_limit - self.current_picked_white_value() + 1
        if self.max_current_ingredient_color('white') < value_needed_to_explode \
                or len(self.ingredients['current']) == 0:
            chance_to_explode = 0
        else:
            explosion_causing_tokens = [
                ingredient for ingredient in self.ingredients['current']
                if ingredient.color == 'white' and ingredient.value >= value_needed_to_explode
            ]
            chance_to_explode = len(explosion_causing_tokens) / len(self.ingredients['current'])

        return chance_to_explode

    def pick_ingredient(self):
        """
        Pick an ingredient at random from those remaining in the bag and remove it.

        Returns
        -------
        selected_ingredient : Ingredient class
            The instance of the selected ingredient.
        """
        selected_ingredient = None

        if len(self.ingredients['current']) > 0:
            selected_ingredient = random.choice(self.ingredients['current'])
            self.ingredients['current'].remove(selected_ingredient)
            self.ingredients['picked'].append(selected_ingredient)
        else:
            print('the bag is empty!')

        return selected_ingredient

    def reset_picked_ingredients(self):
        """Put all picked ingredients back in the bag,
        including those that have been added over the course of the game."""
        self.ingredients['current'] = deepcopy(self.ingredients['master'])
        self.ingredients['picked'] = []

    def add_ingredient(self, color, value):
        """
        Permanently add a single ingredient to the bag.

        Parameters
        ----------
        color : str
            The color of the ingredient to add.
        value : int
            The value of the ingredient token to add.

        Returns
        -------
        Instance of the new Ingredient that is added.
        """
        new_ingredient = Ingredient(color, value)
        self.ingredients['master'].append(new_ingredient)
        return new_ingredient

    def remove_ingredient(self, color, value):
        """
        Permanently remove a single specified ingredient from the bag if it exists.

        Parameters
        ----------
        color : str
            The color of the ingredient to remove.
        value : int
            The value of the ingredient token to remove.

        Returns
        -------
        If one is removed, the instance of the Ingredient class that is removed from the master list
        else None
        """
        potential_ingredients = [
            ingredient for ingredient in self.ingredients['master']
            if ingredient.color == color and ingredient.value == value
        ]

        if len(potential_ingredients) > 0:
            self.ingredients['master'].remove(potential_ingredients[0])
            return potential_ingredients[0]
        else:
            print('There is no ingredient in the bag that matches so none have been removed!')
            return None

    def return_to_baseline(self):
        """Reset the available ingredients back to the starting set."""
        self.ingredients['master'] = []
        self.ingredients['master'].extend([Ingredient('white', value) for value in [1, 1, 1, 1, 2, 2, 3]])
        self.ingredients['master'].extend([Ingredient('orange', value) for value in [1]])
        self.ingredients['master'].extend([Ingredient('green', value) for value in [1]])
        self.reset_picked_ingredients()

    def simulate_round(self, stop_before_explosion=False, risk_tolerance=0):
        """
        Plays out a full round of picking ingredients, adhering to the specified playstyle.

        Parameters
        ----------
        stop_before_explosion : boolean
            Specifies whether the player should stop picking if they know they could explode.
        risk_tolerance : not yet implemented
            To keep pulling, would need less than x% chance of blowing up.

        Returns
        -------
        [int, int]
            List containing the total spaces the player moved, followed by the total whites they ended up with.
        """
        self.reset_picked_ingredients()

        picking = True
        while picking:
            self.pick_ingredient()

            if self.current_picked_white_value() > self.explosion_limit:
                picking = False
            elif stop_before_explosion and self.chance_to_explode() > risk_tolerance:
                picking = False

        overall_total = sum([ingredient.value for ingredient in self.ingredients['picked']])
        white_total = sum([ingredient.value for ingredient in self.ingredients['picked']
                           if ingredient.color == 'white'])

        self.reset_picked_ingredients()

        return [overall_total, white_total]

    def generate_statistics(self, num_rounds=10000, risk_tolerance=0):
        """
        Runs simulated rounds for the bag of ingredients for both playing safe and playing until exploding
        and plots the distribution of results.

        Parameters
        ----------
        num_rounds: int
            The number of rounds to be simulated. By default, set to 10000.
        risk_tolerance: float
            The chance to explode will have to be less than the given value in order to keep picking.
            Will be passed to simulate_round()

        Returns
        -------
        None
        """
        print(f'Running {num_rounds:,} rounds for a bag...\n')
        self.print_ingredients('master')

        exploded_round_values = []
        for i in range(num_rounds):
            temp_round_values = self.simulate_round()
            exploded_round_values.append(temp_round_values[0])
        print(f'\nExploded Maximum score: {np.max(exploded_round_values)}')
        print(f'Exploded Average score: {np.mean(exploded_round_values):.2f}')

        safe_round_values = []
        for i in range(num_rounds):
            temp_round_values = self.simulate_round(stop_before_explosion=True, risk_tolerance=risk_tolerance)
            safe_round_values.append(temp_round_values[0])
        print(f'\nSafe Maximum score: {np.max(safe_round_values)}')
        print(f'Safe Average score: {np.mean(safe_round_values):.2f}')

        exploded_df = pd.DataFrame({'value': exploded_round_values, 'run_type': 'exploded'})
        safe_df = pd.DataFrame({'value': safe_round_values, 'run_type': 'safe'})

        sns.histplot(
            data=pd.concat([exploded_df, safe_df]),
            x='value',
            hue='run_type',
            element='step',
            bins=np.max(exploded_round_values),
            discrete=True
        )
        plt.xlabel('Spaces Moved')
        plt.ylabel('Simulated Occurrences')
        plt.title('Playing Safe vs Picking Until Exploding:\nHow Often Will You Move X Spaces?')
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', labels=['Play Safe', 'Explode'], title='Strategy')

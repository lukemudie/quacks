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
    master_ingredients : list of the Ingredient class
        A list of all ingredients the player has collected.
    current_ingredients : list of the Ingredient class
        A list of all ingredients currently in the player's bag. By default, this will be
        the same as master_ingredients but will change as the player buys more ingredients.
    explosion_limit : int
        The total value of white ingredients that have to be exceeded when pulled in order
        for the player to explode.
    """

    def __init__(self):
        """Initialise the bag with the standard starting ingredients."""
        self.master_ingredients = []
        self.return_to_baseline()
        self.current_ingredients = deepcopy(self.master_ingredients)
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
        ingredients = []
        if set_of_ingredients == 'master':
            ingredients = self.master_ingredients
        elif set_of_ingredients == 'current':
            ingredients = self.current_ingredients
        print(f'Showing the {set_of_ingredients} set of ingredients:')

        unique_colors = list(dict.fromkeys([ingredient.color for ingredient in ingredients]))
        for color in unique_colors:
            print(f'    {color}: ', end='')
            print([ingredient.value for ingredient in ingredients if ingredient.color == color])

    def sum_current_ingredient_color(self, color):
        """Adds up the values of all the tokens of a given color that are in the current ingredients"""
        return sum([ingredient.value for ingredient in self.current_ingredients if ingredient.color == color])

    def max_current_ingredient_color(self, color):
        """Find the max from the values of all the tokens of a given color that are in the current ingredients"""
        return max([ingredient.value for ingredient in self.current_ingredients if ingredient.color == color])

    def pick_ingredient(self):
        """
        Pick an ingredient at random from those remaining in the bag and remove it.

        Returns
        -------
        selected_ingredient : [str, int]
            The selected ingredient token in the form [color, value].
        """
        selected_ingredient = None

        if len(self.current_ingredients) > 0:
            selected_ingredient = random.choice(self.current_ingredients)
            self.current_ingredients.remove(selected_ingredient)
        else:
            print('the bag is empty!')

        return selected_ingredient

    def reset_ingredients(self):
        """Put all picked ingredients back in the bag,
        including those that have been added over the course of the game."""
        self.current_ingredients = deepcopy(self.master_ingredients)

    def add_ingredient(self, color, value):
        """
        Add a single ingredient to the bag.

        Parameters
        ----------
        color : string
            The color of the ingredient.
        value : int
            The value of the ingredient token.

        Returns
        -------
        None
        """
        self.master_ingredients.append(Ingredient(color, value))

    def return_to_baseline(self):
        """Reset the available ingredients back to the starting set."""
        self.master_ingredients = []
        self.master_ingredients.extend([Ingredient('white', value) for value in [1, 1, 1, 1, 2, 2, 3]])
        self.master_ingredients.extend([Ingredient('orange', value) for value in [1]])
        self.master_ingredients.extend([Ingredient('green', value) for value in [1]])
        self.reset_ingredients()

    def simulate_round(self, stop_before_explosion=False, risk_tolerance=0.25):
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
        self.reset_ingredients()

        overall_total = 0
        white_total = 0
        picking = True

        while picking:
            selected = self.pick_ingredient()
            overall_total += selected.value
            if selected.color == 'white':
                white_total += selected.value

            if stop_before_explosion:
                if self.max_current_ingredient_color('white') + white_total > self.explosion_limit:
                    picking = False
            else:
                if white_total > self.explosion_limit:
                    picking = False

        self.reset_ingredients()
        return [overall_total, white_total]

    def generate_statistics(self, num_rounds=10000):
        """
        Runs simulated rounds for the bag of ingredients for both playing safe and playing until exploding
        and plots the distribution of results.

        Parameters
        ----------
        num_rounds: int
            The number of rounds to be simulated. By default set to 10000.

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
            temp_round_values = self.simulate_round(stop_before_explosion=True)
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

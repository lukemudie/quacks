import pandas as pd
import numpy as np
import random
from copy import deepcopy
import warnings
import matplotlib.pyplot as plt
import seaborn as sns


class Player:
    """
    A class used to represent a player in the game.

    Attributes
    ----------
    bag : Bag
        The players bag of ingredients.
    board : Board
        The board that the player is playing on.
    droplet_position : int
        How many spaces round the board the players' droplet is.
    rat_tails : int
        The number of rat tails available to the player.
    has_potion : bool
        Whether the player still has their potion available for use.
    """
    def __init__(self):
        self.bag = Bag()
        self.board = Board()

        self.droplet_position = 0
        self.rat_tails = 0
        self.has_potion = True

    def simulate_round(self, stop_before_explosion=False, risk_tolerance=0):
        """
        Plays out a full round of picking ingredients, adhering to the specified playstyle.

        Parameters
        ----------
        stop_before_explosion : boolean (default False)
            Specifies whether the player should stop picking if they know they could explode.
        risk_tolerance : int (default 0)
            To keep pulling, would need less than x chance of blowing up; probability between 0 and 1.

        Returns
        -------
        dict : {int, int, int}
            'final_position': the position on the board of the last ingredient token placed this round.
            'overall_value': the total value of all ingredients pulled.
            'white_value': the total value of all white ingredients pulled.
        """
        self.bag.reset_picked_ingredients()

        picking = True
        current_position = self.droplet_position + self.rat_tails

        # in the extreme edge case that even the starting configuration is too risky, don't do anything
        if stop_before_explosion and self.bag.chance_to_explode() > risk_tolerance:
            picking = False

        while picking:
            last_picked_ingredient = self.bag.pick_ingredient()

            # will need to expand on this for effects in the future
            current_position += last_picked_ingredient.value

            has_exploded = self.bag.get_picked_white_value() > self.bag.explosion_limit
            has_reached_end = current_position >= self.board.last_playable_space
            has_no_ingredients = len(self.bag.ingredients['current']) == 0
            has_exceeded_risk = stop_before_explosion and self.bag.chance_to_explode() > risk_tolerance

            if has_exploded or has_reached_end or has_no_ingredients or has_exceeded_risk:
                picking = False

            # make sure the last token is not placed beyond the playable space
            if has_reached_end:
                current_position = self.board.last_playable_space

        overall_value = sum([ingredient.value for ingredient in self.bag.ingredients['picked']])
        white_value = sum([ingredient.value for ingredient in self.bag.ingredients['picked']
                           if ingredient.color == 'white'])

        self.bag.reset_picked_ingredients()

        return {
            'final_position': current_position,
            'overall_value': overall_value,
            'white_value': white_value
        }

    def generate_statistics(self, show_ingredients=True, show_graphs=True, num_rounds=10000, risk_tolerance=0):
        """
        Runs simulated rounds for the bag of ingredients for both playing safe and playing until exploding
        and plots the distribution of results.

        Parameters
        ----------
        show_ingredients : bool (default True)
            If True, will print out the master ingredients list to show what the simulations are being run on.
        show_graphs : bool (default True)
            If True, will show the histogram plot of the simulation results at the end.
        num_rounds: int (default 10000)
            The number of rounds to be simulated.
        risk_tolerance: float
            The chance to explode will have to be less than the given value in order to keep picking.
            Will be passed to simulate_round()

        Returns
        -------
        None
        """
        print(f'Running {num_rounds:,} rounds for a bag...')
        if show_ingredients:
            print()
            self.bag.print_ingredients('master')

        exploded_round_values = []
        for i in range(num_rounds):
            temp_round_values = self.simulate_round()
            exploded_round_values.append(temp_round_values['final_position'])
        print(f'\nExploded Maximum score: {np.max(exploded_round_values)}')
        print(f'Exploded Average score: {np.mean(exploded_round_values):.2f}')

        safe_round_values = []
        for i in range(num_rounds):
            temp_round_values = self.simulate_round(stop_before_explosion=True, risk_tolerance=risk_tolerance)
            safe_round_values.append(temp_round_values['final_position'])
        print(f'\nSafe Maximum score: {np.max(safe_round_values)}')
        print(f'Safe Average score: {np.mean(safe_round_values):.2f}')

        if show_graphs:
            exploded_df = pd.DataFrame({'value': exploded_round_values, 'run_type': 'exploded'})
            safe_df = pd.DataFrame({'value': safe_round_values, 'run_type': 'safe'})
            overall_df = pd.concat([exploded_df, safe_df])

            sns.set_theme(style='white', palette='pastel')
            ax = sns.histplot(
                data=overall_df,
                x='value',
                hue='run_type',
                # element='step',
                bins=np.max(exploded_round_values),
                discrete=True
            )

            # getting label values to use for each set (exploded vs safe) such that the bar from that set is only
            # labelled with a number if it is the larger of the two, so that there is only one labelled bar
            # per value on the x-axis
            x_values = list(overall_df['value'].sort_values().unique())
            exploded_labels = []
            safe_labels = []
            for value in x_values:
                exploded_count = exploded_df[['value']].loc[exploded_df['value'] == value].count()[0]
                safe_count = safe_df[['value']].loc[safe_df['value'] == value].count()[0]
                if exploded_count >= safe_count:
                    exploded_labels.append(f'${self.board.money_values[value + 1]}')
                    safe_labels.append('')
                else:
                    exploded_labels.append('')
                    safe_labels.append(f'${self.board.money_values[value + 1]}')

            ax.bar_label(ax.containers[0], safe_labels)
            ax.bar_label(ax.containers[1], exploded_labels)

            plt.xlabel('Place of Final Ingredient Token')
            plt.ylabel('Simulated Occurrences')
            plt.title('Playing Safe vs Picking Until Exploding:\nHow Often Will You Move X Spaces?')
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', labels=['Play Safe', 'Explode'], title='Strategy')


class Board:
    """
    A class used to represent the game board.

    Attributes
    ----------
    point_values : list of int
        A list of the values of points the player gets for finishing in each of the spaces.
    money_values : list of int
        A list of the values of 'money' the player gets for finishing on each of the spaces.
    ruby_values : list of int
        A list of how many rubies the player would get for finishing on each of the spaces.
    is_basic : bool
        Is the player using the basic or advanced side of the board?
    """
    def __init__(self, is_basic=True):
        self.point_values = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6,
                             7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 14, 14, 15]
        self.money_values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15, 16, 16, 17, 17, 18, 18,
                             19, 19, 20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28,
                             29, 29, 30, 30, 31, 31, 32, 32, 33, 33, 35]
        self.ruby_values = [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0,
                            1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0]
        self.is_basic = is_basic
        self.last_playable_space = len(self.money_values) - 1


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

    def print_ingredients(self, set_of_ingredients='current'):
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

    def sum_ingredient_color(self, color, set_of_ingredients='current'):
        """
        Adds up the values of all the tokens of a given color that are in the given list of ingredients.

        Parameters
        ----------
        color : str
            The color of ingredient to sum the values for.
        set_of_ingredients : {'master', 'current', 'picked'} (default 'current')
            The set of ingredients to sum the values for.

        Returns
        -------
        sum : int
            The sum of the values of all the tokens of the given color.
        """
        if set_of_ingredients in ['master', 'current', 'picked']:
            return sum([ingredient.value for ingredient in self.ingredients[set_of_ingredients]
                        if ingredient.color == color])
        else:
            warnings.warn(f"There is no set of ingredients '{set_of_ingredients}', so the sum will be 0.")
            return 0

    def max_ingredient_color(self, color, set_of_ingredients='current'):
        """
        Find the max from the values of all the tokens of a given color that are in the current ingredients.

        Parameters
        ----------
        color : str
            The color of ingredient to find the max value for.
        set_of_ingredients : {'master', 'current', 'picked'} (default 'current')
            The set of ingredients to find the max value for.

        Returns
        -------
        max : int
            The max of the values of all the tokens of the given color.
        """
        if set_of_ingredients in ['master', 'current', 'picked']:
            len_chosen_ingredients = len(self.ingredients[set_of_ingredients])
            colors_chosen_ingredients = list(
                dict.fromkeys([ingredient.color for ingredient in self.ingredients[set_of_ingredients]])
            )
            if len_chosen_ingredients == 0 or color not in colors_chosen_ingredients:
                return 0
            else:
                return max(
                    [ingredient.value for ingredient in self.ingredients[set_of_ingredients] if
                     ingredient.color == color]
                )
        else:
            warnings.warn(f"There is no set of ingredients '{set_of_ingredients}', so the max will be 0.")
            return 0

    def get_picked_white_value(self):
        """Gives the total of all the white ingredients that have been picked so far"""
        return sum([ingredient.value for ingredient in self.ingredients['picked'] if ingredient.color == 'white'])

    def chance_to_explode(self):
        """Get the probability of exploding on the next pick based on what has been picked so far"""
        value_needed_to_explode = self.explosion_limit - self.get_picked_white_value() + 1
        if self.max_ingredient_color('white') < value_needed_to_explode \
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
            warnings.warn(f"There is no ingredient in the bag that matches ({color}, {value}), "
                          f"so none have been removed!")
            return None

    def return_to_baseline(self):
        """Reset the available ingredients back to the starting set."""
        self.ingredients['master'] = []
        self.ingredients['master'].extend([Ingredient('white', value) for value in [1, 1, 1, 1, 2, 2, 3]])
        self.ingredients['master'].extend([Ingredient('orange', value) for value in [1]])
        self.ingredients['master'].extend([Ingredient('green', value) for value in [1]])
        self.reset_picked_ingredients()

"""
Author: Lulof Pirée
May 2022

--------------------------------------------------------------------------------
Copyright (C) 2022 Lulof Pirée

This file is part of the snakes_spn program.

This program is free software:
you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.

--------------------------------------------------------------------------------
File content:
Tools for simulating the Pdn-vs-GbPdn SPN for a wide variety of
different parameter combinations.
"""
from typing import TypeVar, Dict, Sequence, List, Iterator


def run_full_grid_search(rates_all_choices: Dict[str, Sequence[str]],
                         init_markings_all_choices: Dict[str, Sequence[int]],
                         top_level_save_dir: str,
                         num_repetitions: int
                         ):
    # Run repeated sim
    # store log and union of rates and init_markings (all as JSON dicts).
    raise NotImplementedError()


def run_experiment(rates: Dict[str, str],
                   init_markings: Dict[str, int],
                   save_dir: str,
                   num_repetitions: int
                   ) -> Dict[int, Dict[str, Sequence[Number]]]:
    """
    Create a Pdn-vs-GbPdn network with the given rates and initial markings,
    and perform `num_repetitions` independent repetitions.
    Save the log and the hyperparameters
    as "log.json" and "hyperparameters.json" respectively
    in the directory `save_dir`.
    Also return the log.

    @param rates: mapping of transition names to rate formula
        (must be parsable by SNAKES's `Expression` class,
        it may reference variables associated with the places
        that have arcs to the transition).
    @type rates: Dict[str, str]

    @param init_markings: mapping of places to their 
        initial integer token count.
    @type init_markings:  Dict[str, int]

    @param save_dir: path to directory 
        to save the log and the hyperparameter JSON files in.
    @type save_dir: str

    @param num_repetitions: amount of independent repetitions of the simulation.
    @type num_repetitions: int

    @return Dict[int, Dict[str, Sequence[Number]]]: log mapping
        the index of the repetition to a dictionary mapping
        each place to the amount of tokens observed at each timestep,
        and an extra variable "time" mapping to the timestamps
        of simulated-time at each timestep.
    """
    raise NotImplementedError("TODO")


KeyType = TypeVar("KeyType")
ValueToCombine = TypeVar("ValueToCombine")


def get_all_combos(all_values: Dict[KeyType, Sequence[ValueToCombine]]
                   ) -> List[Dict[KeyType, ValueToCombine]]:
    """
    Given a dictionary mapping to sequences of values,
    return a dictionary mapping to one value of the sequence,
    for each possible combination of choices.

    @param all_values: dictionary mapping keys to a sequence of choices.
    @type all_values: Dict[KeyType, Sequence[ValueToCombine]]

    @return List[Dict[KeyType, ValueToCombine]]: sequence containing
        a dictionary for each specific possible combination of choices.
        Return a list of an empty dictionary if `all_values` is empty.
    """
    if len(all_values) == 0:
        return [dict()]

    (key, values) = all_values.popitem()
    output = []
    for value in values:
        new_choice_combo = {key: value}
        other_combos = get_all_combos(all_values.copy())
        for other_combo in other_combos:
            other_combo.update(new_choice_combo)
            output.append(other_combo)
    return output

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
from numbers import Number

import os
import warnings
from spn_tools.run_simulation import (store_log, load_log,
                                      run_repeated_experiment, gen_directories)
from spn_case_study.petrinet import build_gbpdn_spn


import snakes_spn.plugin as spn_plugin
import snakes.plugins
# To prevent autoformatter from putting `from snk ...` at the top of the file.
if True:
    snakes.plugins.load([spn_plugin], "snakes.nets", "snk")
    from snk import PetriNet, Place, Expression, Transition, Variable, tInteger

def run_full_grid_search(rates_all_choices: Dict[str, Sequence[str]],
                         init_markings_all_choices: Dict[str, Sequence[int]],
                         top_level_save_dir: str,
                         num_repetitions: int,
                         max_steps: int,
                         max_time: float,
                         ):
    warnings.warn("TODO: Docstring missing!")
    if not os.path.exists(top_level_save_dir):
        gen_directories(top_level_save_dir)

    exp_idx = 0
    for rates in get_all_combos(rates_all_choices.copy()):
        for init_markings in get_all_combos(init_markings_all_choices.copy()):
            print(f"Starting experiment {exp_idx}")
            dirname = os.path.join(top_level_save_dir, f"exp_{exp_idx}")
            os.mkdir(dirname)
            run_experiment(rates, init_markings, dirname, num_repetitions, 
                           max_steps, max_time)
            exp_idx+=1



def run_experiment(rates: Dict[str, str],
                   init_markings: Dict[str, int],
                   save_dir: str,
                   num_repetitions: int,
                   max_steps: int,
                   max_time: float,
                   ) -> Dict[int, Dict[str, Sequence[Number]]]:
    """
    Create a Pdn-vs-GbPdn network with the given rates and initial markings,
    and perform `num_repetitions` independent repetitions.
    Save the log and the hyperparameters
    as "logs.json" and "hyperparameters.json" respectively
    in the directory `save_dir`.
    Also return the log.

    WARNING: setting neither `max_steps` nor `max_time` 
        might result in an infinitely long simulation, 
        depending on the SPN architecture!

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

    @param max_steps: maximum amount of transition-firings before a repetition
        of the simulation terminates. 
        Use `None` for no limit.
    @type max_steps: Optional[int]

    @param max_time: maximum amount of simulated time.
        This is the cumulative sum of the delays between
        transition firings. The simulation stops after this
        amount of time has passed: it may overshoot it during
        the last step. The value `float("inf")` is allowed
        when no limit on simulated time should be used.
    @type max_time: float

    @return Dict[int, Dict[str, Sequence[Number]]]: log mapping
        the index of the repetition to a dictionary mapping
        each place to the amount of tokens observed at each timestep,
        and an extra variable "time" mapping to the timestamps
        of simulated-time at each timestep.
    """
    spn = build_gbpdn_spn(init_marking=init_markings, rates=rates)
    run_to_log = run_repeated_experiment(num_repetitions, spn, max_steps, 
                                         max_time, verbose=True)
    hyperparams = rates.copy()
    hyperparams.update(init_markings)

    store_log(run_to_log, os.path.join(save_dir, "logs.json"))
    store_log(hyperparams, os.path.join(save_dir, "hyperparameters.json"))

    return run_to_log


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

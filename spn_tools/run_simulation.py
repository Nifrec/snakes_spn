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
Functions to run the simulation of a SPN and
to run N independent repetitions of a simulation.
Also includes a function to save the output to a file.
"""
from __future__ import annotations
import os

from typing import Optional, Dict, Any
import json

import snakes_spn.plugin as spn_plugin
import snakes.plugins
snakes.plugins.load([spn_plugin], "snakes.nets", "snk")
from snk import PetriNet, Place, Expression, Transition, Variable, tInteger

def run_repeated_experiment(num_reps: int,
                            spn: PetriNet,
                            max_steps: Optional[int] = None,
                            max_time: float = float("inf"),
                            verbose: bool = True
                            ) -> dict[int, dict[str, list[float | int]]]:
    run_to_log: Dict[int, dict]
    __print_if(verbose, "Starting repeated experiment "
               f"with {num_reps} repetitions.")
    for run in range(num_reps):
        log = run_simulation(spn, max_steps, max_time)
        run_to_log[run] = log
        __print_if(verbose, f"Finished repetition {run+1}/{num_reps}")
    __print_if(verbose, "All repetitions completed")

    return run_to_log


def __print_if(flag: bool, message: Any):
    if flag:
        print(message)


def run_simulation(spn: PetriNet,
                   max_steps: Optional[int] = None,
                   max_time: float = float("inf")
                   ) -> dict[str, list[float | int]]:
    """
    Simulate a SPN using the Gillespie algorithm either until
    no transitions are enabled, until a maximum amount of steps
    (firings) have been simulated, or until a maximum amount
    of simulated-time has passed.

    @param spn: the Stochastic Petri-Net to simulate.
        Requires the `snakes_spn.plugin` SNAKES-plugin to be loaded!
    @type spn: PetriNet

    @param max_steps: maximum amount of transition-firings before the
        simulation terminates. Use `None` for no limit.
    @type max_steps: Optional[int]

    @param max_time: maximum amount of simulated time.
        This is the cumulative sum of the delays between
        transition firings. The simulation stops after this
        amount of time has passed: it may overshoot it during
        the last step.
        Default value: `float("inf")`.
    @type max_time: float

    @return dict[str, list[float|int]], dictionary mapping
        the names of the places in the SPN to the amount
        of tokens at every step. Also includes a "time" key
        that maps to the timestamp of the simulated time
        (i.e., cumulative delays) per time step.
    """
    places = spn.place()
    log: dict[str, list[float | int]]
    log = {place.name: [] for place in places}
    log.update({"time": []})

    passed_time = 0
    current_timestamp = 0
    if max_steps is not None:
        remaining_steps = max_steps
    else:
        remaining_steps = 1

    while remaining_steps > 0:
        if max_steps is not None:
            remaining_steps -= 1

        current_timestamp += passed_time
        log["time"].append(current_timestamp)
        for place in places:
            log[place.name].append(place.get_num_tokens())

        passed_time = spn.step()  # Returns None when no transition is enabled
        if passed_time is None or current_timestamp >= max_time:
            break

    return log


def store_log(log: dict, filepath: str):
    """
    Store a dictionary to a JSON file.

    @param log: dictionary to save. All contained elements
        must be JSON serializable.
    @type log: dict
    @param filepath: path including filename and .json extension of the
        file to store the log in.
    @type filepath: str
    """
    file_parent_path = os.path.dirname(filepath)
    if not os.path.exists(file_parent_path):
        __gen_directories(file_parent_path)
    assert filepath.endswith(".json")
    
    with open(filepath, "w") as f:
        json.dump(log, f, sort_keys=True)

def __gen_directories(path: str):
    """
    Recursively generate all ancestor directories needed for the given
    path.
    """
    
    if os.path.exists(path):
        print(f"Directory {path} exists.")
        return
    else:
        parent = os.path.dirname(path)
        __gen_directories(parent)
        print(f"Making directory {path}.")
        os.mkdir(path)

def load_log(filepath: str) -> dict:
    """
    Load a JSON file, convert keys in the top-level
    directory to `int` if they can be interpreted as such.

    @param log: dictionary to save. All contained elements
        must be JSON serializable.
    @type log: dict
    @return dict: loaded JSON objects, with keys converted to int
        where possible.
    """
    with open(filepath, "r") as f:
        log: dict = json.load(f)
    
    old_keys = tuple(log.keys())
    for key in old_keys:
        if isinstance(eval(key), int):
            log[eval(key)] = log[key]
            del log[key]

    return log
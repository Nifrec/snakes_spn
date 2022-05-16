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
from snk import PetriNet, Place, Expression, Transition, Variable, tInteger

import snakes_spn.plugin as spn_plugin
import snakes.plugins
snakes.plugins.load([spn_plugin], "snakes.nets", "snk")


def run_repeated_experiment(num_reps: int, spn: PetriNet,
                            max_steps: int, max_time: float
                            ) -> dict[int, dict[str, list[float | int]]]:
    raise NotImplementedError("TODO")


def run_simulation(spn: PetriNet, max_steps: int, max_time: float
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
        simulation terminates.
    @type max_steps: int

    @param max_time: maximum amount of simulated time.
        This is the cumulative sum of the delays between
        transition firings. The simulation stops after this
        amount of time has passed: it may overshoot it during
        the last step.
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
    for _ in range(max_steps):

        current_timestamp += passed_time
        log["time"].append(current_timestamp)
        for place in places:
            log[place.name].append(place.get_num_tokens())

        passed_time = spn.step()  # Returns None when no transition is enabled
        if passed_time is None or current_timestamp >= max_time:
            break

    return log


def store_log(log: dict, filename: str):
    assert filename.endswith(".json")
    raise NotImplementedError("TODO")

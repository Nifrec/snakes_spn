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
import warnings
import numpy as np
from numbers import Number
import math

from collections import OrderedDict
from typing import Optional, Dict, Any, Sequence, Tuple, List, Union
import json

from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from scipy import stats
from scipy.signal import savgol_filter


import snakes_spn.plugin as spn_plugin
import snakes.plugins
# To prevent autoformatter from putting `from snk ...` at the top of the file.
if True:
    snakes.plugins.load([spn_plugin], "snakes.nets", "snk")
    from snk import PetriNet, Place, Expression, Transition, Variable, tInteger


def run_repeated_experiment(num_reps: int,
                            spn: PetriNet,
                            max_steps: Optional[int] = None,
                            max_time: float = float("inf"),
                            verbose: bool = True
                            ) -> dict[int, dict[str, list[float | int]]]:
    run_to_log: Dict[int, dict] = {}
    __print_if(verbose, "Starting repeated experiment "
               f"with {num_reps} repetitions.")
    init_marking = spn.get_marking()
    for run in range(num_reps):
        spn.set_marking(init_marking)
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
        return
    else:
        parent = os.path.dirname(path)
        __gen_directories(parent)
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


def plot_results(run_to_log: Dict[int, Dict[str, List[Number]]],
                 x_var: str | None,
                 y_vars: Sequence[str],
                 num_timeboxes: int,
                 ax: Optional[Axes] = None,
                 conf_ival: float | None = 0.9) -> Axes:
    """
    TODO

    -- x assumed to be sorted
    """
    # if len(x_vars) != len(y_vars):
    #     raise ValueError("Amount of x-variables does not match"
    #         "amount of y-variable collections.")

    # num_subplots = len(x_vars)
    # fix, axes = plt.subpl
    run_to_log = OrderedDict(run_to_log)

    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1)

    # num_timesteps = max([len(log[x_var]) for log in run_to_log.values()])
    timestamps: Dict[int, List[float|int]]
    if x_var is None:
        x_values = list(range(num_timeboxes))
        timebox_size = 1.0
        timestamps = {run_idx:x_values for run_idx in run_to_log.keys()}
    else:
        timestamps = {run_idx: log[x_var] for run_idx, log in run_to_log.items()}
        max_time = max(max(timestamps.values(), key=lambda x : x[-1]))
        timebox_size = max_time/num_timeboxes
        x_values = [(i+0.5)*timebox_size for i in range(num_timeboxes)]

    y_data: Dict[str, List[List[Number]]] = {}
    for y_var_name in y_vars:
        logs = []
        for run_idx in run_to_log.keys():
            timestamps_vector = timestamps[run_idx]
            run_values = run_to_log[run_idx][y_var_name]
            aggregated_run_values = aggregate_in_timeboxes(
                timestamps_vector, run_values, num_timeboxes, timebox_size)
            logs.append(aggregated_run_values)

        print(logs)
        y_data[y_var_name] = logs

    # y_data: Dict[str, List[List[Number]]] = {
    #     y_var_name: [log[y_var_name] for log in run_to_log.values()]
    #     for y_var_name in y_vars
    # }

    

    for y_var_name in y_vars:
        y_mean_values = np.mean(y_data[y_var_name], axis=0)

        ax.plot(x_values, y_mean_values, label=y_var_name)
        warnings.warn("You can't average out on the time like that...\n"
                      "Maybe splitting it in intervals and aggregating each would work.")
        if conf_ival is not None:
            y_std_values = np.std(y_data[y_var_name], axis=0, ddof=1)
            print(y_std_values)
            y_ival_min, y_ival_max = stats.norm.interval(conf_ival,
                                                         loc=y_mean_values,
                                                         scale=y_std_values)
            ax.fill_between(x_values, y_ival_min, y_ival_max,
                            alpha=0.35)

    ax.legend()
    if x_var is not None:
        ax.set_xlabel(x_var)

    return ax


def aggregate_in_timeboxes(timestamps: Sequence[float],
                           measurements: Sequence[float],
                           num_timeboxes: int,
                           timebox_size: float) -> Sequence[float]:
    """
    Take `m` pairs of a timestamp `t` and a measurement `y`
    (where the timestamps may not be evenly spaced!),
    and compute an aggregation with evenly spaced time boxes.
    In particular, return a vector `v` of `num_timeboxes`
    values, where each value `v[i]` is the average of all
    measurements with timestamps `t` s.t.
    `i*timebox_size <= t < (i+1)*timebox_size`.
    If no measurement is available for some time-interval
    `[i*timebox_size, (i+1)*timebox_size]`, use the value `v[i-1]` instead.
    If the first measurements are missing, simply use 0 instead.

    NOTE: it is assumed that the timestamps and the measurements
    are sorted in chronological order. If this is not the case,
    the output will be incorrect.

    @param timestamps: vector of timestamps corresponding to each measurement.
    @type timestamps: Sequence[float]

    @param measurements: vector of measured values
        corresponding to the timestamps.
    @type measurements: Sequence[float]

    @param num_timeboxes: amount of indices in the output,
        corresponding to the time-intervals with `timebox_size` spacing.
    @type num_timeboxes: int

    @param timebox_size: width of each time interval
        (i.e., amount of time between beginnings of consecutive timeboxes).
    @type timebox_size: float

    @return: Sequence[float], aggregated measurements.
    """
    assert len(measurements) == len(timestamps)

    timebox_endtimes = [i * timebox_size for i in range(1, 1+num_timeboxes)]

    # Index of the current timebox
    curr_timebox = 0
    # Amount of measurements added to the current timebox
    # (Needed for averaging them later -- they are just summed up)
    num_points_added = 0

    output = [0 for _ in range(num_timeboxes)]

    for i in range(len(measurements)):
        while timestamps[i] >= timebox_endtimes[curr_timebox]:
            __agg_curr_timebox(output, curr_timebox, num_points_added)

            num_points_added = 0
            curr_timebox += 1

            if curr_timebox >= num_timeboxes:
                return output

        output[curr_timebox] += measurements[i]
        num_points_added += 1

    __agg_curr_timebox(output, curr_timebox, num_points_added)

    if curr_timebox != num_timeboxes-1:
        for remaining_box in range(curr_timebox, num_timeboxes):
            output[remaining_box] = output[curr_timebox]
    return output


def __agg_curr_timebox(output: Sequence[float],
                       curr_timebox: int,
                       num_points_added: int):
    """
    Resolve the definite aggregated value for the current timebox.
    """
    if num_points_added == 0 and curr_timebox == 0:
        output[curr_timebox] = 0
    elif num_points_added == 0:
        output[curr_timebox] = output[curr_timebox-1]
    elif num_points_added > 0:
        output[curr_timebox] = output[curr_timebox]/num_points_added

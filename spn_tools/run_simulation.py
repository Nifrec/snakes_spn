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
from typing import Literal, Optional, Dict, Any, Sequence, Tuple, List, Union
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
    """
    Same as `run_simulation()`, but repeats the simulation
    from the initial marking `num_reps` times.
    The output is a dictionary mapping each repetition-index
    in [0, `num_reps`-1] to the output log of that simulation.

    @param num_reps: amount of independent 
        repetitions of the simulation from the starting state.
    @type num_reps: int

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

    @param verbose: flag whether progress should be printed.
    @type verbose: bool

    @return dict[int, dict[str, list[float | int]]], dictionary mapping
        index of the repetition to the output of the simulation
        (as returned by `run_simulation()`).
    """
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
        gen_directories(file_parent_path)
    assert filepath.endswith(".json")

    with open(filepath, "w") as f:
        json.dump(log, f, sort_keys=True)


def gen_directories(path: str):
    """
    Recursively generate lowest and all ancestor directories 
    in the given path path.

    @param: path, file system path to generate. Missing directories
        will be created.
    @type path: str
    """

    if os.path.exists(path) or path=="":
        return
    else:
        parent = os.path.dirname(path)
        gen_directories(parent)
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
                 x_var: str,
                 y_vars: Sequence[str],
                 num_timeboxes: int,
                 ax: Optional[Axes] = None,
                 interval_type: Literal["min_max", "confidence"] | None
                 = "min_max",
                 conf_ival: float | None = 0.9) -> Axes:
    """
    Create plots of desired variables,
    averaged over multiple independent runs.
    The x-variable gives the timestamps, which do not need to be the
    same for each run.

    Takes as input a mapping of a run index to a dictionary
    mapping a variable name to the recorded values during that run.
    The y-variables and the x_var must be keys in these dictionaries.
    Values are aggregated in time-boxes of uniform length
    for each run
    (like a histogram, but then taking the average value instead
    of the number of observations),
    and then averaged over the different runs.

    The x_var gives the variable to use for the horizontal axis.
    This will usually be the time variable.
    The data in each run of this variable must be sorted
    (usually this means ascending time),
    and the maximum value observed over the whole dataset for this
    variable is used to determine the width of the time-boxes
    (i.e., if the maximum value is `T` then the width of the time-boxes
        is `T / num_timeboxes`).
    In the plot, also the x-variable is aggregated in time-boxes.
    (This is needed to average out the y-values, which does
    not work out of the box for measurements with a different set of
    timestamps each run!).

    @param run_to_log: collection of independent repetitions of an experiment,
        each repetition is stored as a dictionary mapping the name
        of a variable to a vector of observed values
        (in chronological order, by x-variable). 
    @type run_to_log: Dict[int, Dict[str, List[Number]]]

    @param x_var: name of the x-variable ('time-variable'),
        key in the dictionaries in `run_to_log`.
    @type x_var: str

    @param y_vars: names of the y-variables to plot.
        All must be keys in `run_to_log`.
        Each will be plotted in the same subfigure,
        and labelled by their name.
    @type y_vars: Sequence[str]

    @param ax: optional Matplotlib `Axes` instance to plot graph in.
        If `None`, a new `Axes` instance is created and returned.
    @type ax: matplotlib.axes.Axes | None

    @param interval_type: uncertainty interval around the graph 
        mean-value lines. Can be left out (value `None`),
        the minimum and maximum observed values in each timebox
        (value `'min_max'`), or a `100*conf_ival`% confidence interval
        using a local normal approximation in each timebox.
    @type interval_type: Literal["min_max", "confidence"] | None

    @param conf_ival: value in [0, 1]
        such that the width of the uncertainty interval
        around the graphs is a `100*conf_ival`% confidence interval
        around the mean. Only used when `interval_type='confidence'`.
    @type conf_ival: float | None

    @return Axes: Matplotlib axis in which the graphs are drawn.
        This is the input argument `ax` if it was not `None`,
        and a new `Axes` otherwise.
    """
    warnings.warn("TODO: cleanup!")
    run_to_log = OrderedDict(run_to_log)

    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1)

    timestamps: Dict[int, List[float | int]]
    timestamps = {run_idx: log[x_var] for run_idx, log in run_to_log.items()}
    max_time = max(max(timestamps.values(), key=lambda x: x[-1]))
    timebox_size = max_time/num_timeboxes
    x_values = [(i+0.5)*timebox_size for i in range(num_timeboxes)]

    y_data = __find_y_data(y_vars, timestamps, run_to_log, num_timeboxes,
                           timebox_size)

    for y_var_name in y_vars:
        y_mean_values = np.mean(y_data[y_var_name], axis=0)

        ax.plot(x_values, y_mean_values, label=y_var_name)
        if interval_type == "min_max":
            y_ival_min = np.min(y_data[y_var_name], axis=0)
            y_ival_max = np.max(y_data[y_var_name], axis=0)
        elif interval_type == "confidence":
            y_std_values = np.std(y_data[y_var_name], axis=0, ddof=1)
            y_ival_min, y_ival_max = stats.norm.interval(conf_ival,
                                                         loc=y_mean_values,
                                                         scale=y_std_values)
        elif interval_type is not None:
            raise ValueError("Unknown interval type '{interval_type}'.")
        if interval_type is not None:
            ax.fill_between(x_values, y_ival_min, y_ival_max,
                            alpha=0.35)

    ax.legend()
    if x_var is not None:
        ax.set_xlabel(x_var)

    return ax


def __find_y_data(y_vars: Sequence[str],
                  timestamps: Dict[int, List[float]],
                  run_to_log: Dict[int, Dict[str, List[Number]]],
                  num_timeboxes: int,
                  timebox_size: float) -> Dict[str, List[List[Number]]]:
    """
    For each requested variable, collect all the vectors
    of observations in a list (i.e., a matrix, whose rows
    are the measurements during a specific experiment),
    and apply the timebox-aggregation.
    """
    y_data: Dict[str, List[List[Number]]] = {}
    for y_var_name in y_vars:
        logs = []
        for run_idx in run_to_log.keys():
            timestamps_vector = timestamps[run_idx]
            run_values = run_to_log[run_idx][y_var_name]
            aggregated_run_values = aggregate_in_timeboxes(
                timestamps_vector, run_values, num_timeboxes, timebox_size)
            logs.append(aggregated_run_values)

        y_data[y_var_name] = logs
    return y_data


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

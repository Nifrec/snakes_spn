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
Tests for the file `spn_tools/run_simulation.py`.
"""

import json
import shutil
import numpy as np
from spn_tools.run_simulation import (aggregate_in_timeboxes, run_simulation, store_log, load_log,
                                      run_repeated_experiment, plot_results)

import unittest
import matplotlib.pyplot as plt
import os


import snakes_spn.plugin as spn_plugin
import snakes.plugins
# To prevent autoformatter from putting `from snk ...` at the top of the file.
if True:
    snakes.plugins.load([spn_plugin, "gv"], "snakes.nets", "snk")
    from snk import PetriNet, Place, Expression, Transition, Variable, tInteger

PLOT_FILENAME = os.path.join("snakes_spn", "test", "run_sim_graph.pdf")
GRAPH_FILENAME = os.path.join("snakes_spn", "test", "simple_spn.pdf")

class StoreLogTestCase(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join("snakes_spn", "test", "dummy_dir",
                                 "test_log.json")
        self.log = {
            0: {"a": 2, "b": 4},
            1: [1, 2, 3],
            2: "Hello world!"
        }

    def tearDown(self):
        shutil.rmtree(os.path.join("snakes_spn", "test", "dummy_dir"))

    def test_save_and_load(self):
        store_log(self.log, self.path)
        self.assertTrue(os.path.exists(self.path))
        loaded_log = load_log(self.path)
        self.assertDictEqual(loaded_log, self.log)


class RunSimulationTestCase(unittest.TestCase):

    def test_run_simulation_til_dead_state(self):
        """
        Use a simple SPN that has a clear fixed amount
        of possible transitions (with only 1 possible choice each timestep)
        before it reaches a dead state
        to test the size of the output `run_simulation()`.
        """
        num_input_tokens = 36
        spn = make_simple_spn(num_input_tokens)
        output = run_simulation(spn)
        self.assertIsInstance(output, dict)
        # +1, because the initial state should also be included in the output.
        expected_len = num_input_tokens + 1
        self.assertSequenceEqual(output["sink"],
                                 [x for x in range(expected_len)])
        self.assertSequenceEqual(
            output["source"], [x for x in range(num_input_tokens, -1, -1)])

        for i in range(expected_len - 1):
            self.assertGreater(output["time"][i+1], output["time"][i])


class MultiRunPlotTestCase(unittest.TestCase):
    LOG_PATH = os.path.join("snakes_spn", "test",
                            "run_sim_files", "run_to_log.json")

    def setUp(self):
        if not os.path.exists(self.LOG_PATH):
            spn = make_simple_spn()
            self.num_runs = 30
            run_to_log = run_repeated_experiment(self.num_runs, spn)
            store_log(run_to_log, self.LOG_PATH)
        self.log = load_log(self.LOG_PATH)

    def test_plot_results(self):
        num_timeboxes = max(map(lambda x: len(x["time"]), self.log.values()))
        num_timeboxes //= 2
        print(num_timeboxes)
        ax = plot_results(self.log, "time", ["source", "sink"], num_timeboxes)
        plt.show()


class AggregateInTimeboxesTestCase(unittest.TestCase):
    """
    Tests for `aggregate_in_timeboxes()`.
    """

    def test_aggregate_in_timeboxes_no_vals_for_first_boxes(self):
        """
        Corner case: no measurements for first few boxes.

        Measurements:
        [3,     4,      6,      7,      8,      9,      10]
        Timestamps:
        [1,     1.1,    1.2,    2.1,    2.2,    2.7,    3.0]

        Num timeboxes: 7
        Timebox size: 0.5

        Expected:
        [0,     0,      13/3,   13/3,   7.5,    9,      10]
        End times:
        [0.5,   1.0,    1.5,    2.0,    2.5,    3.0,    3.5]
        """
        measurements = [3, 4, 6, 7, 8, 9, 10]
        timestamps = [1,  1.1, 1.2, 2.1, 2.2, 2.7, 3.0]
        num_timeboxes = 7
        timebox_size = 0.5
        expected = [0, 0, 13/3.0, 13/3.0, 7.5, 9, 10]

        result = aggregate_in_timeboxes(timestamps, measurements, num_timeboxes,
                                        timebox_size)
        np.testing.assert_allclose(result, expected)

    def test_aggregate_in_timeboxes_no_vals_last_boxes(self):
        """
        Corner case: no measurements available for the last timeboxes.

        Measurements:
        [1,     2,      3,      4]
        Timestamps:
        [0.3,   0.7,    0.9,    1.1]


        Num timeboxes: 7
        Timebox size: 0.5

        Expected:
        [1,     2.5,    4,      4,      4,      4,      4]
        End times:
        [0.5,   1.0,    1.5,    2.0,    2.5,    3.0,    3.5]
        """
        measurements = [1,     2,      3,      4]
        timestamps = [0.3,   0.7,    0.9,    1.1]
        num_timeboxes = 7
        timebox_size = 0.5
        expected = [1,     2.5,    4,      4,      4,      4,      4]

        result = aggregate_in_timeboxes(timestamps, measurements, num_timeboxes,
                                        timebox_size)
        np.testing.assert_allclose(result, expected)


def plot_run_simulation_results():
    output = run_simulation(make_simple_spn())

    fig, axes = plt.subplots(nrows=2, ncols=1)

    x = output["time"]
    source = output["source"]
    sink = output["sink"]
    ax = axes[0]
    ax.plot(x, source, label="source")
    ax.plot(x, sink, label="sink")
    ax.set_title("Tokens over time")

    ax = axes[1]
    ax.plot(x)
    ax.set_title("timestamps")
    ax.set_xlabel("timestep")
    ax.set_ylabel("Timestamp")

    fig.tight_layout()
    fig.savefig(PLOT_FILENAME)
    plt.show()


def make_simple_spn(num_input_tokens: int = 36) -> PetriNet:
    """
    Construct a simple network with one transition.
    """

    spn = PetriNet("TestRunSimulationNet")
    spn.add_place(Place("source", num_input_tokens, tInteger))
    spn.add_place(Place("sink", 0, tInteger))
    spn.add_transition(Transition("source_to_sink",
                                  guard=Expression("c_source>=1"),
                                  rate_function=Expression("c_source")))

    spn.add_input("source", "source_to_sink", Variable("c_source"))
    spn.add_input("sink", "source_to_sink", Variable("c_sink"))

    spn.add_output("source", "source_to_sink", Expression("c_source-1"))
    spn.add_output("sink", "source_to_sink", Expression("c_sink+1"))
    return spn

def graph_simple_spn():
    spn=make_simple_spn()
    spn.draw(GRAPH_FILENAME)


if __name__ == "__main__":
    if not os.path.exists(PLOT_FILENAME):
        plot_run_simulation_results()

    unittest.main()

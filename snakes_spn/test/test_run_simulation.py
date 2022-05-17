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
from spn_tools.run_simulation import run_simulation, store_log, load_log

import unittest
import matplotlib.pyplot as plt
import os

import snakes_spn.plugin as spn_plugin
import snakes.plugins
snakes.plugins.load([spn_plugin], "snakes.nets", "snk")
from snk import PetriNet, Place, Expression, Transition, Variable, tInteger

PLOT_FILENAME = os.path.join("snakes_spn", "test", "run_sim_graph.pdf")

class StoreLogTestCase(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join("snakes_spn", "test", "dummy_dir", "test_log.json")
        self.log = {
            0: {"a":2, "b":4},
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

def plot_results():
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


def make_simple_spn(num_input_tokens: int=36) -> PetriNet:
    """
    Construct a simple network with one transition"
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

if __name__ == "__main__":

    if not os.path.exists(PLOT_FILENAME):
        plot_results()

    unittest.main()

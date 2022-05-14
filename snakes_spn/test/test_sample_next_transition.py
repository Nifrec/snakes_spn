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
Testcase for the modified `PetriNet` class with the SPN
features of the plugin added.
"""


from snakes_spn.test.testing_tools import H2_INIT, H2O_INIT, O2_INIT, Fe2O3_INIT, Fe_INIT, Ti_INIT, TiO2_INIT, draw_graph, draw_graph_advanced_net, setup_advanced_spn, ADVANCED_GRAPH_FILENAME

import unittest
from snakes.data import Substitution
import os

# Import and activate the plugin (and the rest of SNAKES)
import snakes_spn.plugin as spn_plugin
import snakes.plugins
snakes.plugins.load([spn_plugin, "gv"], "snakes.nets", "snk")
from snk import *

import matplotlib.pyplot as plt
PLOT_FILENAME = os.path.join("snakes_spn", "test", "observed_delays.pdf")

class GetNextTransitionTestCase(unittest.TestCase):

    def test_sample_next_transition(self):
        """
        From the initial concentrations, 
        we would expect rates and probabilities:

        reaction | formula              |   rate | probability
        1.          O2+2H2->2H20            10000   66.6667%
        2.          4Fe + 3O2 -> 2Fe2O3     5000    33.3333%
        3.          Ti + 02 -> TiO2         0       0%

        Plots histograms of observed delays.
        (Note that the PetriNet is never fired, so the rates remain constant.)
        """
        num_trials = 15000

        observed_freqs = {
            "4Fe+3O2->2Fe2O3": 0,
            "Ti+02->TiO2": 0,
            "O2+2H2->2H20": 0
        }

        observed_delays = {
            "4Fe+3O2->2Fe2O3": [],
            "Ti+02->TiO2": [],
            "O2+2H2->2H20": []
        }

        expected_modes = {
            "O2+2H2->2H20": Substitution({"conc_H2": H2_INIT,
                                          "conc_O2": O2_INIT,
                                          "conc_H2O": H2O_INIT}),
            "4Fe+3O2->2Fe2O3": Substitution({"conc_Fe": Fe_INIT,
                                             "conc_O2": O2_INIT,
                                             "conc_Fe2O3": Fe2O3_INIT}),
            "Ti+02->TiO2": Substitution({"conc_Ti": Ti_INIT,
                                         "conc_O2": O2_INIT,
                                         "conc_TiO2": TiO2_INIT})
        }

        spn = setup_advanced_spn()

        for trial in range(num_trials):
            trans_name, mode, delay = spn.sample_next_transition()

            observed_freqs[trans_name] += 1
            self.assertEqual(expected_modes[trans_name], mode)

            observed_delays[trans_name].append(delay)
        
        self.assertAlmostEqual(observed_freqs["O2+2H2->2H20"]/num_trials, 0.66, delta=0.05)
        self.assertAlmostEqual(observed_freqs["4Fe+3O2->2Fe2O3"]/num_trials, 0.33, delta=0.05)
        self.assertEqual(observed_freqs["Ti+02->TiO2"], 0)

        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(5, 15))

        axes[0].hist(observed_delays["O2+2H2->2H20"], bins=50)
        axes[0].set_title("O2+2H2->2H20")
        axes[1].hist(observed_delays["4Fe+3O2->2Fe2O3"], bins=50)
        axes[1].set_title("4Fe+3O2->2Fe2O3")
        axes[2].hist(observed_delays["Ti+02->TiO2"], bins=50)
        axes[2].set_title("Ti+02->TiO2")
       

        plt.show()

        # fig.savefig(PLOT_FILENAME)

    def test_error_no_transition_available(self):
        """
        `PetriNet.sample_next_transition()` should raise a `SnakesError`
        when no transition is enabled.
        """
        # Only products have tokens, bo reactants are available.
        spn = setup_advanced_spn(0, 0, 100, 0, 0, 100, 100)
        with self.assertRaises(SnakesError):
            spn.sample_next_transition()


if __name__ == "__main__":

    if not os.path.exists(ADVANCED_GRAPH_FILENAME):
        draw_graph_advanced_net()
    unittest.main()

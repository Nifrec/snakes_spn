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
Reusable methods for building testcases.
Mostly definitions of specific Stochastic Petri-Nets.
"""
import os
# Import and activate the plugin (and the rest of SNAKES)
import snakes_spn.plugin as spn_plugin
import snakes.plugins
snakes.plugins.load([spn_plugin, "gv"], "snakes.nets", "snk")
from snk import *

GRAPH_FILENAME = os.path.join("snakes_spn", "test", "spn_oxygen_hydrogen.pdf")

# Initial 'concentrations'
O2_INIT = 100
H2_INIT = 100



def setup_test_net(init_hydrogen: int = H2_INIT,
                   init_oxygen: int = O2_INIT) -> PetriNet:
    spn = PetriNet("spn_oxygen_hydrogen")

    spn.add_place(Place("hydrogen", init_hydrogen, tInteger))
    spn.add_place(Place("oxygen", init_oxygen, tInteger))
    spn.add_place(Place("water", 0, tInteger))

    spn.add_transition(
        Transition("O2+2H2->2H20",
                   guard=Expression("conc_H2 >=2 and conc_O2 >= 1"),
                   rate_function=Expression("conc_H2 * conc_O2")))

    spn.add_input("hydrogen", "O2+2H2->2H20", Variable("conc_H2"))
    spn.add_input("oxygen", "O2+2H2->2H20", Variable("conc_O2"))
    spn.add_input("water", "O2+2H2->2H20", Variable("conc_H2O"))

    spn.add_output("hydrogen", "O2+2H2->2H20", Expression("conc_H2 - 2"))
    spn.add_output("oxygen", "O2+2H2->2H20", Expression("conc_O2 - 1"))
    spn.add_output("water", "O2+2H2->2H20", Expression("conc_H2O + 2"))

    return spn


def draw_graph():
    """
    Print the SPN used for testing graphically to a PDF file.
    """
    spn = setup_test_net()
    spn.draw(GRAPH_FILENAME)
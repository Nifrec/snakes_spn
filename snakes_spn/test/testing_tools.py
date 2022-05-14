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
from snk import PetriNet, Place, Transition, tInteger, Expression, Variable

GRAPH_FILENAME = os.path.join("snakes_spn", "test", "spn_oxygen_hydrogen.pdf")
ADVANCED_GRAPH_FILENAME = os.path.join("snakes_spn", "test", "spn_multi_transition.pdf")
# Initial 'concentrations'
O2_INIT = 100
H2_INIT = 100
H2O_INIT = 0
Fe_INIT = 50
Ti_INIT = 0
Fe2O3_INIT = 0
TiO2_INIT = 0


def setup_test_net(init_hydrogen: int = H2_INIT,
                   init_oxygen: int = O2_INIT,
                   init_water : int = H2O_INIT) -> PetriNet:
    spn = PetriNet("spn_oxygen_hydrogen")

    spn.add_place(Place("hydrogen", init_hydrogen, tInteger))
    spn.add_place(Place("oxygen", init_oxygen, tInteger))
    spn.add_place(Place("water", init_water, tInteger))

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

def setup_advanced_spn(init_hydrogen: int = H2_INIT,
                   init_oxygen: int = O2_INIT,
                   init_water : int = H2O_INIT,
                   init_iron: int = Fe_INIT,
                   init_titanium: int = Ti_INIT,
                   init_hematite: int = Fe2O3_INIT,
                   init_titaniumdioxide: int = TiO2_INIT) -> PetriNet:
    """
    Create a PetriNet for the following reactions*:
    1. O2+2H2->2H20
    2. 4Fe + 3O2 -> 2Fe2O3
    3. Ti + 02 -> TiO2


    * They might not be chemically accurate, but that isn't the point here.
    """
    spn = setup_test_net(init_hydrogen, init_oxygen, init_water)

    spn.add_place(Place("iron", init_iron, tInteger))
    spn.add_place(Place("hematite", init_hematite, tInteger))
    spn.add_place(Place("titanium", init_titanium, tInteger))
    spn.add_place(Place("titaniumdioxide", init_titaniumdioxide, tInteger))

    spn.add_transition(Transition("4Fe+3O2->2Fe2O3",
                   guard=Expression("conc_Fe >= 4 and conc_O2 >= 3"),
                   rate_function=Expression("conc_Fe * conc_O2")))
    spn.add_input("iron", "4Fe+3O2->2Fe2O3", Variable("conc_Fe"))
    spn.add_input("hematite", "4Fe+3O2->2Fe2O3", Variable("conc_Fe2O3"))
    spn.add_input("oxygen", "4Fe+3O2->2Fe2O3", Variable("conc_O2"))
    spn.add_output("iron", "4Fe+3O2->2Fe2O3", Expression("conc_Fe-4"))
    spn.add_output("oxygen", "4Fe+3O2->2Fe2O3", Expression("conc_O2-3"))
    spn.add_output("hematite", "4Fe+3O2->2Fe2O3", Expression("conc_Fe2O3+2"))


    spn.add_transition(Transition("Ti+02->TiO2",
                   guard=Expression("conc_Ti >= 1 and conc_O2 >= 2"),
                   rate_function=Expression("conc_Ti * conc_O2")))
    spn.add_input("titanium", "Ti+02->TiO2", Variable("conc_Ti"))
    spn.add_input("titaniumdioxide", "Ti+02->TiO2", Variable("conc_TiO2"))
    spn.add_input("oxygen", "Ti+02->TiO2", Variable("conc_O2"))
    spn.add_output("titanium", "Ti+02->TiO2", Expression("conc_Ti-1"))
    spn.add_output("oxygen", "Ti+02->TiO2", Expression("conc_O2-2"))
    spn.add_output("titaniumdioxide", "Ti+02->TiO2", Expression("conc_TiO2+1"))

    return spn

def draw_graph_advanced_net():
    """
    Print the 'advanced' SPN used for testing graphically to a PDF file.
    """
    spn = setup_advanced_spn()
    spn.draw(ADVANCED_GRAPH_FILENAME)

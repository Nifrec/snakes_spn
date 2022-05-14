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
Empirical test on the 'advanced testing network' to see if the
SPN (esp. the `PetriNet.step()`) function behaves as expected.
"""
from typing import List
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

def main():
    spn = setup_advanced_spn()
    conc = {place.name : [place.get_num_tokens()] for place in spn.place()}
    timestamps: List[float] = [0]

    cumul_time = 0
    delay = 0
    while True:
        delay = spn.step()
        if delay is None:
            break
        cumul_time += delay
        timestamps.append(cumul_time)

        for place in spn.place():
            conc[place.name].append(place.get_num_tokens())

    print(f"Simulation finished after {len(timestamps)} steps")

    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(timestamps, conc["oxygen"], label="$O_2$", color="red")
    ax.plot(timestamps, conc["hydrogen"], label="$H_2$", color="green")
    ax.plot(timestamps, conc["water"], label="$H_2O$", color="blue")
    ax.set_xlabel("Time")
    ax.set_ylabel("Concentration")
    ax.set_title(r"$2H_2 + O_2 \rightarrow H_2O$")
    ax.legend()

    plt.show()


if __name__ == "__main__":
    main()

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
Testcases for `run_grid_search.py`.
"""


import json
import shutil
import numpy as np
from spn_tools.run_simulation import (aggregate_in_timeboxes, run_simulation, store_log, load_log,
                                      run_repeated_experiment, plot_results)

import unittest


import snakes_spn.plugin as spn_plugin
import snakes.plugins
if True:
    snakes.plugins.load([spn_plugin], "snakes.nets", "snk")
    from snk import PetriNet, Place, Expression, Transition, Variable, tInteger

from spn_case_study.run_grid_search import get_all_combos

class GetAllCombosTestCase(unittest.TestCase):

    def test_empty_input(self):
        """
        Empty input should return a list of an empty dict: `[{}]`.
        """
        expected = [dict()]
        result = get_all_combos(dict())
        self.assertListEqual(expected, result)

    def test_base_case(self):
        inp_dict = {
            "a":["a_1", "a_2", "a_3"],
            "b":["b_1", "b_2"],
            "c":["c_1"]
        }

        expected = [
            {"a":"a_1", "b":"b_1", "c":"c_1"},
            {"a":"a_2", "b":"b_1", "c":"c_1"},
            {"a":"a_3", "b":"b_1", "c":"c_1"},
            {"a":"a_1", "b":"b_2", "c":"c_1"},
            {"a":"a_2", "b":"b_2", "c":"c_1"},
            {"a":"a_3", "b":"b_2", "c":"c_1"},
        ]

        result = get_all_combos(inp_dict)
        self.assertListEqual(expected, result)

if __name__ == "__main__":
    unittest.main()

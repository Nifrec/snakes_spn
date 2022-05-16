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
Testcase of the `create_guard()` function in `case_study/petrinet.py`.
"""

import unittest
from spn_case_study.petrinet import create_guard, VARS

class CreateGuardTestCase(unittest.TestCase):

    def test_create_guard(self):
        places = ("pdn", "gbpdn", "gba2")
        result = create_guard(places, VARS)
        expected = "c_pdn>=1 and c_gbpdn>=1 and c_gba2>=1"
        self.assertEqual(result, expected)
        

if __name__ == "__main__":
    unittest.main()
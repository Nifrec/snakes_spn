"""
Author: Lulof Pirée
June 2022

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
Testcases for `spn_case_study/auxiliary_tools.py`.
"""

import unittest

from spn_case_study.auxiliary_tools import strip_prefix_number_from_string

class StripPrefixNumberFromStringTestCase(unittest.TestCase):

    def test_float_case(self):
        inp_str = "0.01234Hello World"
        expected = "0.01234"
        result = strip_prefix_number_from_string(inp_str)
        self.assertEqual(result, expected)

    def test_int_case(self):
        inp_str = "456Unicorn123"
        expected = "456"
        result = strip_prefix_number_from_string(inp_str)
        self.assertEqual(result, expected)

    def test_error_case(self):
        inp_str = "Dragons999"
        with self.assertRaises(ValueError):
            strip_prefix_number_from_string(inp_str)

if __name__ == "__main__":
    unittest.main()
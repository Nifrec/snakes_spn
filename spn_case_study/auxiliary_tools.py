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
Collection of reusable auxiliary functions 
relevant for the Pdn-GbPdn case-study experiments.
"""
import re

def strip_prefix_number_from_string(inp_str: str) -> str:
    """
    Given a string that starts with a positive number
    (an int or a float, so either with or without the decimal point.
    No scientific notation, hexadecimal, sign-symbols, etc.),
    return the string representing this number.
    Raise a ValueError if `inp_str` has no prefix that
    can be interpreted as a number.

    >>> strip_prefix_number_from_string("0.01234Hello World")
    "0.01234"

    >>> strip_prefix_number_from_string("456Unicorn123")
    "456"
    
    @param rate_str: string to strip numeric prefix off.
    @type rate_str: str

    @return str: number that is the longest prefix of rate_str
        that can be interpreted as a number.
    """
    pattern = r"^\d+(\.\d+)?"
    match = re.match(pattern, inp_str)
    if match is not None:
        return match.group(0)
    else:
        raise ValueError(
            f"String {repr(inp_str)} does not start with a number.")
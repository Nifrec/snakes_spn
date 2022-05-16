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
Dictionary-like class that only allows specific keys,
and for each key only values of a given type.
These keynames-values are given as an argument during initialization.
This class is well-suited for settings or hyperparameters,
where values of the wrong type, or a typing mistake in the variable name,
can cause problems.
"""
from __future__ import annotations
from typing import *
from copy import deepcopy

import os
DEFAULT_RDICT_FILENAME = "RestrictedDict.txt"


class RestrictedDict:

    """
    Dictionary-like class that maps strings
    to variables of any type.
    However, the type that belongs to a variable's name is fixed,
    and so is the set of possible variable names.

    Variables can be accessed directly as members.
    E.g. if an instance `my_obj` of `RestrictedDict`
    has a variable `"foo"`, it can be accessed as `my_obj.foo`.
    """

    def __init__(self, variables: dict[str, type], values: dict[str, Any] = {}):
        """
        Arguments:
        * variables: set of allowed variables (keys, as strings)
            in this dictionary, and the corresponding
            type it is allowed to have.
        * values: dictionary of initial values of (a subset of)
            the variables specified in `variables`.
            Naturally, their values must map their corresponding
            types as described in `variables`.

        """
        self.__variables = variables

        # Set of variables that currently have an assigned value.
        # This is a subset of self.__variables.keys()
        self.__present_variables: set[str] = set()

        for (var_name, value) in deepcopy(values).items():
            self[var_name] = value

    @property
    def variables(self) -> dict[str, type]:
        return self.__variables.copy()

    @property
    def present_variables(self) -> set[str]:
        return self.__present_variables.copy()

    def __getitem__(self, var_name: str) -> Any:
        """
        Get the value of the variable with name `var_name`.
        """
        self.__check_var_exists(var_name)
        if var_name not in self.__present_variables:
            raise KeyError(f"No value set for variable '{var_name}'.")
        return self.__getattribute__(var_name)

    def __setitem__(self, var_name: str, value: Any):
        """
        Assign a new value `value` to the variable with name `var_name`.
        Raise an error if `var_name` is not a key in `self.variables`,
        or when `value` is not an allowed type.
        """
        self.__check_valid_assignment(var_name, value)
        self.__setattr__(var_name, value)
        self.__present_variables.add(var_name)

    def __check_valid_assignment(self, var_name: str, value: Any):
        """
        Check if the given (var_name, value) pair is
        according to the variables specified in `self.variables`.
        I.e., raise an error if the `var_name` is not a valid variable name,
        or if `value` is of the wrong type.
        Raise an error if one of the above checks fail.

        Arguments:
        * var_name: name of the variable to assign the value `value`,
            must be a key in `self.variables`.
        * value: value to assign to the variable `var_name`.
        """
        self.__check_var_exists(var_name)
        self.__check_valid_type(var_name, value)

    def __check_var_exists(self, var_name: str):
        if var_name not in self.__variables.keys():
            raise KeyError(f"Unknown variable '{var_name}'")

    def __check_valid_type(self, var_name: str, value: Any):
        if not isinstance(value, self.__variables[var_name]):
            raise TypeError(f"Variable {var_name} of type {type(value)},"
                            f" expected {self.__variables[var_name]}")

    def save_to_disk(self, directory_name: str,
                     filename: str = DEFAULT_RDICT_FILENAME):
        """
        Save a text representation of `self`
        in a file `filename` (by default, "RestrictedDict.txt")
        in the indicated file directory.
        """
        if filename is None:
            filename = self.DEFAULT_FILENAME

        if not os.path.exists(directory_name):
            os.mkdir(directory_name)

        filename = os.path.join(directory_name, filename)
        with open(filename, mode="w+") as f:
            f.write(repr(self))

    @staticmethod
    def load_from_disk(directory_name: str,
                       file_name: str = DEFAULT_RDICT_FILENAME
                       ) -> RestrictedDict:
        filename = os.path.join(directory_name, file_name)

        with open(filename, mode="r") as f:
            str_representation: str = f.read()
        output: RestrictedDict = eval(str_representation)
        return output

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        outp = "RestrictedDict(\n\tvariables={\n"
        for var_name, var_type in self.variables.items():
            outp += f"\t\t{repr(var_name)}:{var_type.__name__},\n"
        outp += "\t},\n\tvalues={\n"
        for var_name in self.__present_variables:
            value_repr = self.__get_repr_value(self[var_name])
            outp += f"\t\t{repr(var_name)}:{value_repr},\n"
        outp += "\t}\n)"
        return outp

    def __get_repr_value(self, var_value: Any) -> str:
        """
        Calling `repr()` does not provide the right Python code for all
        objects. For example, `repr(float('inf')) = 'inf',
        which is a string and not a number.
        """
        if var_value == float('inf'):
            return "float('inf')"
        else:
            return repr(var_value)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, (RestrictedDict, dict)):
            return False

        output = True
        for var_name in self.present_variables:
            try:
                other_value = other[var_name]
            except KeyError:
                return False
            output &= self[var_name] == other_value
        return output

    def copy(self) -> RestrictedDict:
        """
        Make a *shallow* copy with the same variables and values.
        """
        values = {var_name: self[var_name]
                  for var_name in self.present_variables}
        return RestrictedDict(self.variables, values)

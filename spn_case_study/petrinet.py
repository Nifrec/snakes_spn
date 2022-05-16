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
Definitions and construction of the SPN 
of the Pdn-vs-GbPdn bio-modelling case study.
"""
from spn_simulation_tools.restricted_dict import RestrictedDict

from typing import Dict, Tuple


from collections import namedtuple

import snakes_spn.plugin as spn_plugin
import snakes.plugins
snakes.plugins.load([spn_plugin, "gv"], "snakes.nets", "snk")
from snk import PetriNet, Place, Expression, Transition, Variable, tInteger

# Names of the places of the Petri-Net
place_field_names = ("pdn", "gbpdn", "gba2", "gr_free", "gr_pdn", "gr_gbpdn",
                     "neutrophil_free", "neutrophil_inflaming")
default_place_names = ("Pdn", "GbPdn", "Gba2", "Gr", "Gr.Pdn", "Gr.GbPdn",
                       "Free Neutrophils", "Recruited Neutrohils")
PlaceNames = namedtuple("PlaceNames", field_names=place_field_names,
                        defaults=default_place_names)
PLACES = PlaceNames()

# Names of the variables as used in SNAKES to mark arcs.
VariableNames = namedtuple("VariableNames", field_names=place_field_names,
                           defaults=["c_" + name for name in place_field_names])
VARS = VariableNames()

# Names of the transitions
trans_field_names = ("prod_gba2", "decay_gba2", "cleave", "decay_pdn",
                     "bind_pdn", "unbind_pdn", "decay_gbpdn", "bind_gbpdn",
                     "unbind_gbpdn", "recruit_neutrophil")
TransNames = namedtuple("TransNames", field_names=trans_field_names,
                        defaults=trans_field_names)
TRANS = TransNames()

# Mapping of transition name to the place_field_name of incoming places.
TRANS_TO_PLACES: Dict[str, Tuple[str, ...]] = {
    "prod_gba2":("gba2"),
    "decay_gba2":("gba2"),
    "cleave": ("pdn", "gbpdn", "gba2"),
    "decay_pdn": ("pdn"),
    "bind_pdn":("pdn", "gr", "gr_pdn"),
    "unbind_pdn":("pdn", "gr", "gr_pdn"),
    "decay_gbpdn": ("gbpdn"), 
    "bind_gbpdn" : ("gbpdn", "gr", "gr_gbpdn"),
    "unbind_gbpdn":("gbpdn", "gr", "gr_gbpdn"),
    "recruit_neutrophil":("gr_pdn", "neutrophil_free", "neutrophil_inflaming")
}

# Mapping that defines (1) the accepted hyperparameter names
# and (2) what type each hyperparameter ought to be of.
HYPERPARAM_VARS = {
    # Rates are strings describing a formula
    # that are can be used to construct an Expression.
    # When representing concentrations of certain places,
    # ensure that variable names from `VARS` are used in these rates.
    (trans_name + "_rate") : str for trans_name in trans_field_names
}



def build_pdn_net(hyperparams: Dict,
                  place_names: PlaceNames = PLACES,
                  var_names: VariableNames = VARS,
                  trans_names: TransNames = TRANS,
                  init_marking: Dict[str, int] = {name: 0 for name in PLACES},
                  trans_to_places: Dict[str, Tuple[str, ...]] =TRANS_TO_PLACES
                  ) -> PetriNet:

    place_names_set = set(place_names)
    for trans, places in TRANS_TO_PLACES.items():
        assert trans in trans_names
        assert place_names_set.issubset(places)

    # This automatically checks if the hyperparameter names are known,
    # and if they of the correct type. Values could still be bogus though.
    params = RestrictedDict(HYPERPARAM_VARS, hyperparams)
    spn = PetriNet("Pdn_vs_GbPdn_competition")

    place: str
    for place in place_names:
        spn.add_place(Place(place, init_marking[place], check=tInteger))
    
    for trans in trans_names:
        rate = Expression(params[trans+"_rate"])
        places = trans_to_places[trans]
        guard_str = print()
        guard = Expression()
        spn.add

    return spn

def create_guard(place_names: Tuple[str, ...], var_names: VariableNames) -> str:
    """
    Construct a guard indicating that the variables (amount of tokens) 
    of the given places must all be at least 1.
    That is, given `n` places, construct a string
    `"x_0>=1 and x_1>=1 and" ... "x_n>=0"`
    where `x_0`, `x_1`, ..., `x_n` whose corresponding variable names
    for the places.

    @param place_names: names of places whose variables should
        be in the guard. Must be a subset of the attributes of `VariableNames`.
    @type place_names: Tuple[str, ...]
    @param var_names: namedtuple mapping place names to their corresponding
        variables.
    @type var_names: VariableNames

    @return guard: str, string that evaluates to a logical formula
        being true if and only if the amount of tokens of the 
        of the given places is at least 1.
    """
    if len(place_names) == 0:
        return ""
    var_names = var_names._asdict()
    output = f"{var_names[place_names[0]]}>=1"
    for place in place_names[1:]:
        output += " and "
        output += f"{var_names[place]}>=1"
    return output

if __name__ == "__main__":
    print(PLACES)
    print(VARS)
    spn = build_pdn_net()
    print(spn)

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

from typing import Dict, Iterable, Tuple, TypedDict, Set
import itertools

from collections import namedtuple

import snakes_spn.plugin as spn_plugin
import snakes.plugins
snakes.plugins.load([spn_plugin, "gv"], "snakes.nets", "snk")
from snk import PetriNet, Place, Expression, Transition, Variable, tInteger

# Names of the places of the Petri-Net
place_field_names = ("pdn", "gbpdn", "gba2", "gr_free", "gr_pdn", "gr_gbpdn",
                     "neutrophil_free", "neutrophil_inflaming")
PLACES = place_field_names

# Names of the variables as used in SNAKES to mark arcs.
VariableNames = TypedDict(
    "VariableNames", {name: str for name in place_field_names})
VARS: VariableNames = {name: f"c_{name}" for name in place_field_names}

# Names of the transitions
trans_field_names = ("prod_gba2", "decay_gba2", "cleave", "decay_pdn",
                     "bind_pdn", "unbind_pdn", "decay_gbpdn", "bind_gbpdn",
                     "unbind_gbpdn", "recruit_neutrophil")
TRANS = trans_field_names


class ArcDict(TypedDict, total=False):
    """
    Simple record to keep track which places are connected to a transition,
    and whether they donate or consume tokens.
    """
    # Places that neither donate nor consume a token,
    # but that are still relevant for the guard or the rate of the transition.
    read_arcs: Tuple[str, ...]
    # Places that donate a token each time the transition fires
    # (a pre-arc with weight 1 in a formal Petri-Net)
    pre_arcs: Tuple[str, ...]
    # Places that receive a token each time the transition fires
    # (a post-arc with weight 1 in a formal Petri-Net)
    post_arcs: Tuple[str, ...]

    def get_all_places(self) -> Tuple[str]:
        return tuple(itertools.chain(self.read_arcs, self.pre_arcs, self.post_arcs))


# Mapping of transition name to the place_field_name of incoming places.
TRANS_TO_PLACES: Dict[str, ArcDict] = {
    "prod_gba2": {"post_arcs": ("gba2",)},
    "decay_gba2": {"pre_arcs": ("gba2",), },
    "cleave": {"read_arcs": ("gba2",),
               "pre_arcs": ("gbpdn",),
               "post_arcs": ("pdn",)},
    "decay_pdn": {"pre_arcs": ("pdn",), },
    "bind_pdn": {"pre_arcs": ("pdn", "gr_free"),
                 "post_arcs": ("gr_pdn",)},
    "unbind_pdn": {"pre_arcs": ("gr_pdn",),
                   "post_arcs": ("pdn", "gr_free")},
    "decay_gbpdn": {"pre_arcs": ("gbpdn",), },
    "bind_gbpdn": {"pre_arcs": ("gr_free", "gbpdn"), "post_arcs": ("gr_gbpdn",)},
    "unbind_gbpdn": {"pre_arcs": ("gr_gbpdn",), "post_arcs": ("gr_free", "gbpdn")},
    "recruit_neutrophil": {"read_arcs": ("gr_pdn",),
                           "pre_arcs": ("neutrophil_free",),
                           "post_arcs": ("neutrophil_inflaming",)}
}

def get_all_places(arc_dict: ArcDict) -> Set[str]:
    return set(itertools.chain(*arc_dict.values()))

# RatesDict = TypedDict("RatesDict", {trans: str for trans in TRANS})


def build_spn(place_names: Tuple[str, ...] = PLACES,
              var_names: Dict[str, str] = VARS,
              trans_names: Tuple[str, ...] = TRANS,
              rates: Dict[str, str] = {trans: "0" for trans in TRANS},
              init_marking: Dict[str, int] = {name: 0 for name in PLACES},
              trans_to_places: Dict[str, ArcDict] = TRANS_TO_PLACES,
              ) -> PetriNet:
    """
    Construct a Stochastic Petri-Net with unit-weight arcs according
    to the given specification.

    Initial values construct the Pdn-vs-GbPdn case-study network.
    However, this function can be used for any other SPN.

    @param place_names: names of the places of the SPN.
    @type place_names: Tuple[str, ...]
    
    @param var_names: mapping of place name in `place_names`
        to name of that place's arcs.
        These are variables in guards and rates of transitions.
    @type var_names: Dict[str, str]
    
    @param trans_names: names of the transitions of the SPN.
    @type trans_names: Tuple[str, ...]
    
    @param rates: mapping of transition names in `trans_names`
        to a string representing a numerical computation,
        which may include the var_names of the connected places
        (will be wrapped in a SNAKES `Expression`).
    @type rates: Dict[str, str]

    @param init_marking: mapping of places (in `place_names`) 
        to initial amount of tokens.
    @type init_marking: Dict[str, int]

    @param trans_to_places : mapping of transition names in `trans_names`
        to the places that have arcs to this transition.
        Expected keys: 
        * "read_arcs", maps to places whose token count is not
            affected by this transition.
        * "pre-arcs", maps to places whose token count is decreased by 1.
        * "post-arcs", maps to places whose token count is increased by 1.
        Values should be iterables with elements in `place_names`.
    @type trans_to_places: Dict[str, ArcDict]

    @return spn: PetriNet, Stochastic Petri-Net with above features.
    """

    place_names_set: Set[str] = set(place_names)
    trans: str
    for trans, arc_dict in TRANS_TO_PLACES.items():
        assert trans in trans_names
        places = set(get_all_places(arc_dict))
        assert place_names_set.issuperset(places), \
            f"{places} contains unknown places"

    spn = PetriNet("Pdn_vs_GbPdn_competition")

    place: str
    for place in place_names:
        spn.add_place(Place(place, init_marking[place], check=tInteger))

    for trans in trans_names:
        rate = Expression(rates[trans])
        arc_dict = trans_to_places[trans]
        places = get_all_places(arc_dict)
        guard_str = create_guard(places, var_names)
        guard = Expression(guard_str)
        spn.add_transition(Transition(trans, guard=guard, rate_function=rate))

        for place in places:
            spn.add_input(place, trans, Variable(var_names[place]))

        if "pre_arcs" in arc_dict.keys():
            for place in arc_dict["pre_arcs"]:
                spn.add_output(place, trans, Expression(f"{var_names[place]}-1"))

        if "post_arcs" in arc_dict.keys():
            for place in arc_dict["post_arcs"]:
                spn.add_output(place, trans, Expression(f"{var_names[place]}+1"))
    return spn


def create_guard(place_names: Iterable[str], var_names: Dict[str, str]) -> str:
    """
    Construct a guard indicating that the variables (amount of tokens) 
    of the given places must all be at least 1.
    That is, given `n` places, construct a string
    `"x_0>=1 and x_1>=1 and" ... "x_n>=0"`
    where `x_0`, `x_1`, ..., `x_n` whose corresponding variable names
    for the places.

    @param place_names: names of places whose variables should
        be in the guard. Must be a subset of the keys of `var_names`.
    @type place_names: Tuple[str, ...]
    @param var_names: mapping of place names to their corresponding
        variables.
    @type var_names: Dict[str, str]

    @return guard: str, string that evaluates to a logical formula
        being true if and only if the amount of tokens of the 
        of the given places is at least 1.
    """
    place_names = tuple(place_names)
    if len(place_names) == 0:
        return ""
    output = f"{var_names[place_names[0]]}>=1"
    for place in place_names[1:]:
        output += " and "
        output += f"{var_names[place]}>=1"
    return output


if __name__ == "__main__":
    print(RatesDict)
    print(PLACES)
    print(VARS)
    spn = build_spn(rates)
    print(spn)
    spn.draw("test.pdf")

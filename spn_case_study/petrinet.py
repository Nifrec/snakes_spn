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



from typing import Dict, Iterable, Tuple, TypedDict, Set
import itertools

from collections import namedtuple

import snakes_spn.plugin as spn_plugin
from spn_tools.build_spn import build_spn, ArcDict
import snakes.plugins
snakes.plugins.load([spn_plugin, "gv"], "snakes.nets", "snk")
from snk import PetriNet, Place, Expression, Transition, Variable, tInteger

# Names of the places of the Petri-Net
place_field_names = ("pdn", "gbpdn", "gba2", "gr_free", "gr_pdn", "gr_gbpdn",
                     "neutrophil_free", "neutrophil_inflaming")
PLACES = place_field_names

# Names of the variables as used in SNAKES to mark arcs.
VARS = {name: f"c_{name}" for name in place_field_names}

# Names of the transitions
trans_field_names = ("prod_gba2", "decay_gba2", "cleave", "decay_pdn",
                     "bind_pdn", "unbind_pdn", "decay_gbpdn", "bind_gbpdn",
                     "unbind_gbpdn", "recruit_neutrophil")
TRANS = trans_field_names


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


def build_gbpdn_spn(place_names: Tuple[str, ...] = PLACES,
                    var_names: Dict[str, str] = VARS,
                    trans_names: Tuple[str, ...] = TRANS,
                    rates: Dict[str, str] = {trans: "0" for trans in TRANS},
                    init_marking: Dict[str, int] = {
                        name: 0 for name in PLACES},
                    trans_to_places: Dict[str, ArcDict] = TRANS_TO_PLACES,
                    ) -> PetriNet:
    """
    Wrapper for `spn_tools.build_spn()` with initial values for the 
    Pnd-vs-GbPdn case study network.
    """
    return build_spn(place_names, var_names, trans_names,
                     rates, init_marking, trans_to_places)


if __name__ == "__main__":
    spn = build_gbpdn_spn()
    print(spn)
    spn.draw("test.pdf")

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
Small runnable script for configuring and launching the Pnd-vs-GbPdn experiment.
"""
import time
import os
from typing import Dict, Sequence
from spn_case_study.petrinet import PLACES, VARS, TRANS, TRANS_TO_PLACES
from spn_case_study.run_grid_search import run_experiment, run_full_grid_search

GBA2_PROD_CONST = 1
GBA2_DECAY_CONST = 0
PDN_DECAY_CONST = 0
GBPDN_DECAY_CONST = 0
CLEAVE_CONST = 1
PDN_BIND_CONST = 1
GBPDN_BIND_CONST = PDN_BIND_CONST / 1000
PDN_UNBIND_CONST = 1
GBPDN_UNBIND_CONST = 1
NEUTROPHIL_RECRUIT_CONST = 1

REPRESS_INFL_CONST = 1

NUM_REPETITIONS = 20
MAX_NUM_TRANSITIONS = 500
MAX_TIME_PASSED = 5


def main():
    timestamp = time.strftime(r"%Y-%m-%d_%H-%M-%S", time.localtime())
    savedir_name = os.path.join("test_runs",timestamp)
    run_full_grid_search(setup_rates_all_choices(),
                         setup_init_markings_all_choices(),
                         savedir_name, NUM_REPETITIONS,
                         MAX_NUM_TRANSITIONS, MAX_TIME_PASSED)


def setup_init_markings_all_choices() -> Dict[str, Sequence[int]]:
    output = {name: (0,) for name in PLACES}

    output["gba2"] = (1000,)
    output["gbpdn"] = (1000,)
    output["neutrophil_free"] = (1000,)
    output["gr_free"] = (1000,)
    return output


def setup_rates_all_choices() -> Dict[str, Sequence[str]]:
    output = {}

    # Decay reactions: all use the Mass-action Law
    output["decay_gba2"] = f"{GBA2_DECAY_CONST}*{VARS['gr_pdn']}"
    output["decay_pdn"] = f"{PDN_DECAY_CONST}*{VARS['pdn']}"
    output["decay_gbpdn"] = f"{GBPDN_DECAY_CONST}*{VARS['gbpdn']}"

    # TODO: Cleavage -- mass-action??? Michaelis-Menten?
    output["cleave"] = f"{CLEAVE_CONST}*{VARS['gba2']}*{VARS['gbpdn']}"

    # Binding -- Mass Action
    output["bind_pdn"] = f"{PDN_BIND_CONST}*{VARS['pdn']}*{VARS['gr_free']}"
    output["bind_gbpdn"] = f"{GBPDN_BIND_CONST}*{VARS['gbpdn']}*{VARS['gr_free']}"

    # Unbinding -- Mass Action
    output["unbind_pdn"] = f"{PDN_UNBIND_CONST}*{VARS['gr_pdn']}"
    output["unbind_gbpdn"] = f"{GBPDN_UNBIND_CONST}*{VARS['gr_gbpdn']}"

    output["repress_infl"] = f"{REPRESS_INFL_CONST} * {VARS['gr_pdn']}"

    # TODO: Neutrophil recruitment.
    # Does attractment slow down the more neutrophils are already present?
    # This would cause exponentially decaying growth 
    # (assuming constant `infl_sig`): 
    # f"{NEUTROPHIL_RECRUIT_CONST}*{VARS['neutrophil_free']}*{VARS['infl_sig']}"
    output["recruit_neutrophil"] = (
        # Linear growth:
        f"{NEUTROPHIL_RECRUIT_CONST}*{VARS['infl_sig']}",        
    )

    for key in output.keys():
        if isinstance(output[key], str):
            output[key] = (output[key],)
    return output


if __name__ == "__main__":
    main()
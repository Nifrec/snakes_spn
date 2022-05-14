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
Python script providing the SPN features to the SNAKES plugin interface.
"""
from __future__ import annotations
from typing import *
from types import ModuleType
import random
import math

from snakes import ConstraintError
import snakes.plugins
from snakes.data import Substitution
from snakes.nets import Expression, Token
import snakes.nets


def gen_transition_class(module: ModuleType) -> Type[snakes.nets.Transition]:
    """
    Given a configured version of `snakes.net` as `module`,
    create a new subclass of `module.Transition` with SPN features.

    @param module: Python module providing a subclassable class `Transition`.
    @type module: types.ModuleType
    @return: subclass of `snakes.nets.Transition` with SPN features.
    """

    class Transition(module.Transition):

        def __init__(self, name, guard, **args) -> None:
            """

            @param args: plugin arguments
            @keyword stats: initial status of the Transition 
                (defaults to `TransitionStatus(False, None)`)
            @type status: Optional[TransitionStatus]
            @keyword rate_function: expression computing the 
                current rate of the exponentially-distributed delay.
            @type rate_function: Expression
            """
            self._rate = args.pop("rate_function")
            assert isinstance(self._rate, Expression)
            module.Transition.__init__(self, name, guard, **args)

        def get_current_rate(self, binding: Substitution) -> float:
            """
            Compute the current rate (AKA 'lambda') of the exponentially
            distributed delay of this transition in a Stochastic Petri Net.
            Note that `1/rate` gives the expected delay until firing.

            @param binding: current evaluation of Variables of incoming
                arcs in the Petri-Net.
            @type binding: Substitution
            @return: float, positive number giving the current rate.
            """
            current_rate: Token = self._rate.bind(binding)
            return float(current_rate.value)

    return Transition


def gen_petrinet_class(module: ModuleType) -> Type[snakes.nets.PetriNet]:
    """
    Given a configured version of `snakes.net` as `module`,
    create a new subclass of `module.PetriNet` with SPN features.
    (These features are stepping in time, and sampling the next transition
    delay).

    @param module: Python module providing a subclassable class `Transition`.
    @type module: types.ModuleType
    @return: subclass of `snakes.nets.Transition` with SPN features.
    """

    class PetriNet(module.PetriNet):

        def sample_next_transition(self) -> Tuple[str, Substitution, float]:
            """
            Sample the next transition to fire,
            using an exponential distribution of the delay for each transition,
            with as parameter the rate given by the transition.
            This follows Gillespie's algorithm
            (see, e.g., 
                p141, chapter 7 by Ivan Mura in the book
                'Modeling in Systems Biology The Petri Net Approach' 
                (2011, Springer-Verlag London Limited)
                editors I. Kock, W. Reisig and F. Schreiber
            ).

            If multiple modes are possible for a given transition,
            only the first mode is considered.

            @return name: str, name of the transition to fire
            @return binding: Substitution, the variable binding
                to be used in the chosen transition.
            @return time_passed: float, the time passed
                until the given transition since the previous
                transition (or start of the simulation).
                Note that this assumes 
                memoryless exponentially distributed delays.
            """
            transitions = {trans.name(): trans.modes()
                           for trans in self.transition()}

            # Lists of names, modes (Substitutions/bindings) and rates
            # of all enabled transitions.
            enabled_transitions: List[str] = []
            enabled_modes: List[Substitution] = []
            enabled_rates: List[float] = []
            for trans_name in transitions:
                if len(transitions[trans_name]) > 0:
                    enabled_transitions.append(trans_name)
                    # Use first possible variable binding.
                    # For most SPN applications there
                    # will probably be only one anyway.
                    mode = transitions[trans_name][0]
                    enabled_modes.append(mode)
                    rate = self.transition[trans_name].get_current_rate(mode)
                    enabled_rates.append(rate)

            if len(enabled_transitions) == 0:
                raise RuntimeError("No transition is enabled.")
            # When considering multiple independent exponential distributions
            # with parameters (= event-occurrence rates) r_1, r_2, ..., r_n,
            # then the time until the first event in any of them occurs
            # is exponentially distributed
            # with rate `r = r_1 + r_2 + ... + r_n`.
            sum_rates = sum(enabled_rates)
            # Cumulative density function: `probability ~ e^{-rate * delay}`.
            # So using probability u ~ uniform[0, 1),
            # then we can sample a delay as
            # `delay = -ln(u) / rate`.
            delay = -math.log(random.random()) / sum_rates

            # For a given enabled transition with rate `rate`,
            # the probability that this is the transition firing next
            # is `rate / sum_rates`. This sums nicely to 1 over all
            # transitions. It is a property of exponential distributions.
            u = random.random()
            trans_idx = 0
            cum_prob = enabled_rates[trans_idx] / sum_rates
            while cum_prob < u:
                trans_idx += 1
                cum_prob += enabled_rates[trans_idx] / sum_rates

            assert 0 < cum_prob <= 1, \
                "Cannot happen: cumulative probability exceeded 1"

            output = (enabled_transitions[trans_idx],
                      enabled_modes[trans_idx],
                      enabled_rates[trans_idx])
            return output


@snakes.plugins.plugin("snakes.nets")
def extend(module: ModuleType) -> Tuple[Type[snakes.nets.Transition], Type[snakes.nets.PetriNet]]:

    Transition = gen_transition_class(module)

    return Transition

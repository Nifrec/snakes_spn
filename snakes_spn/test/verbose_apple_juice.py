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
Extremely simple Petri-Net (not stochastic)
to explore how SNAKES works internally.

Idea: 3 apples + 1 empty bottle make 1 bottle of apple juice.

Result of experiment: when reading and changeing variables,
    they are removed and added back.
"""
import snakes.plugins
snakes.plugins.load("gv", "snakes.nets", "snk")
from snk import *
from snakes.nets import Place, Transition, Variable, Expression, Value
from snakes.typing import tInteger

class VerbosePlace(Place):
    """
    Subclass of SNAKES's Place that prints some information.
    """

    def add(self, tokens):
        print("Pre-add tokens:", self.tokens)
        print("Added tokens:", tokens)
        super().add(tokens)
        print("Post-add tokens:", self.tokens)

    def remove(self, tokens):

        print("Pre-remove tokens:", self.tokens)
        print("Removed tokens:", tokens)
        super().remove(tokens)
        print("Post-remove tokens:", self.tokens)




def main():
    pn = PetriNet("juice_factory")

    pn.add_place(Place("bottle", 10, tInteger))
    pn.add_place(VerbosePlace("apple", 30, tInteger))
    pn.add_place(Place("apple_juice", 0, tInteger))

    pn.add_transition(Transition("apple_press", guard=Expression("b>=1 and a >= 3")))

    pn.add_input("bottle", "apple_press", Variable("b"))
    pn.add_input("apple", "apple_press", Variable("a"))
    pn.add_input("apple_juice", "apple_press", Variable("j"))
    pn.add_output("bottle", "apple_press", Expression("b-1"))
    pn.add_output("apple", "apple_press", Expression("a-3"))
    pn.add_output("apple_juice", "apple_press", Expression("j+1"))

    pn.draw("juice_factory.pdf")

    fire_modes = pn.transition("apple_press").modes()
    while len(fire_modes) > 0:
        pn.transition("apple_press").fire(fire_modes[0])
        print(f"Apples: {pn.place('apple').tokens},"
            f" \tempty bottles: {pn.place('bottle').tokens},"
            f" \tbottles of juice: {pn.place('apple_juice').tokens}")
        fire_modes = pn.transition("apple_press").modes()
    
    print("`Place.post` and `Place.pre` give sets of "
        "outgoing- and incoming-arcs, respectively, for the given place.")
    print(pn.place("apple").post, pn.place("apple").pre)

if __name__ == "__main__":
    main()
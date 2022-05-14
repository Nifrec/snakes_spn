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
Outdated data type.
My first idea was to sample delays beforehand, store them in the transitions,
and then search for the next delay every simulation step
(quite like the timed Petri-Net example plugin from the SNAKES website).
However, Gillespie's algorithm is more efficient, 
simpler (~= less room for bugs) and easier to implement/test,
so I changed plans and used that instead.
"""

class TransitionStatus:

    def __init__(self, is_running: bool = False, remaining_delay: float | None = None):
        self.is_running: bool = is_running
        self.remaining_delay: float | None = remaining_delay

    @property
    def is_running(self) -> bool:
        return self.is_running

    @is_running.setter
    def is_running(self, new_value: bool):
        self.is_running = new_value
        if not self.is_running:
            self.remaining_delay = None

    @property
    def remaining_delay(self) -> float | None:
        if not self.is_running:
            raise RuntimeError("TransitionStatus has no remaining delay "
                               "while not running.")
        return self.is_running

    @remaining_delay.setter
    def remaining_delay(self, new_delay: float | None):
        if isinstance(new_delay, float) and not self.is_running:
            raise RuntimeError("Cannot set delay when not running.")
        if isinstance(new_delay, None) and self.is_running:
            raise RuntimeError("While running, the delay must be a number.")
        self.remaining_delay = new_delay

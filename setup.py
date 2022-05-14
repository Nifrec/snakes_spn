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
Code to setup the repository as an installable Python package.
"""

from setuptools import setup, find_packages

__author__ = "Lulof Pirée"
__version__ = "v1.0.0"

setup(name='snakes_spn',
      author=__author__,
      author_email="lulof.piree@zoho.com",
      description="Stochastic Petri-Net plugin for the SNAKES library",
      version=__version__,
      packages=find_packages())

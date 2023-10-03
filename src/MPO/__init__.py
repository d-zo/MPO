# -*- coding: utf-8 -*-
"""

  M a t e r i a l  -  P a r a m e t e r  -  O p t i m i e r u n g
 |      \/      |      |     ___     \         .´   .---.   `.
 |   |\    /|   |      |    |___)    /        /    /     \    \
 |   | \__/ |   |      |     _____.-´         \    \     /    /
 |   |      |   |      |    |                  \    `---´    /
 |___|      |___|      |____|                   `._________.´

 D.Zobel 2020-2023      v0.4

Parameter-Optimierung anhand von Oedometer- oder Triaxialversuchen
"""

# Copyright 2020-2023 Dominik Zobel.
# All rights reserved.
#
# This file is part of the MPO package.
# MPO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MPO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MPO. If not, see <http://www.gnu.org/licenses/>.


from .hilfen import *
from .dateneinlesen import *
from .optionsverarbeitung import *
from .versuchsliste import *
from .abweichung import *
from .plotausgabe import *
from .programmsteuerung import *

__author__ = 'Dominik Zobel'
__version__ = '0.4'
__package__ = 'MPO'



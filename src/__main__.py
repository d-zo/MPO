# -*- coding: utf-8 -*-
"""
__main__.py   v0.3
2023-02 Dominik Zobel
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


# Paketname muss explizit angegeben werden, wenn mit relativen Abhaengigkeiten gearbeitet wird.
# Diese sind wiederum fuer ein Laden der Bibliotheken aus einem zip-Archiv (.pyz) erforderlich
__package__ = 'MPO'


# -------------------------------------------------------------------------------------------------
def main(argumente):
   """Diese Funtion startet MPO und ruft alle notwendigen Funktionen auf.
   """
   import os
   import time
   from .optionsverarbeitung import Optionen_verarbeiten
   from .dateneinlesen import JSONDateiEinlesen
   from .versuchsliste import Versuchsliste_Erstellen_Und_Speichern
   from .abweichung import Bodendaten_Und_Vergleichsdaten, Bewerte_Ergebnisse
   from .programmsteuerung import Berechne_Variationen
   from .plotausgabe import Plots_Erstellen
   #
   print('Starte MPO minimal v0.4      (Startzeit ' + time.strftime('%Y-%m-%d %H:%M') + ')')
   #
   optionen = Optionen_verarbeiten(argumente=argumente)
   if (optionen is None):
      return
   #
   einstellungen = JSONDateiEinlesen(dateiname='einstellungen.json')
   if (einstellungen is None):
      return
   #
   if (not os.path.isdir(einstellungen['Arbeitsverzeichnis'])):
      os.makedirs(einstellungen['Arbeitsverzeichnis'])
   #
   if (optionen['cmd'] != 'nutze_liste'):
      if (not Versuchsliste_Erstellen_Und_Speichern(einstellungen=einstellungen)):
         return
      #
      if (optionen['cmd'] == 'liste_erstellen'):
         return
   #
   letzter_durchlauf = None
   gesamtbodendaten = []
   #
   startzeit = time.time()
   #
   schluessel = sorted(list(einstellungen['Versuchsablauf'].keys()))
   num_durchlaeufe = len(schluessel)
   for idx_durchlauf in range(num_durchlaeufe):
      print('\n# ----------------------------------------')
      print('# --- Lauf ' +  str(idx_durchlauf+1) + '/' + str(num_durchlaeufe) + '\n')
      #
      str_durchlauf = schluessel[idx_durchlauf]
      #
      bodendaten, vergleichsdaten = Bodendaten_Und_Vergleichsdaten(einstellungen=einstellungen,
         str_versuch=str_durchlauf)
      if (vergleichsdaten is None):
         print('Vergleichsdaten leer')
         return
      #
      gesamtbodendaten += [bodendaten]
      #
      Berechne_Variationen(einstellungen=einstellungen, vergleichsdaten=vergleichsdaten,
         str_versuch=str_durchlauf)
   #
   print('\n# ----------------------------------------')
   indizes = Bewerte_Ergebnisse(einstellungen=einstellungen)
   #
   if (indizes == []):
      print('# Keine brauchbaren Ergebnisse zum Plotten')
   else:
      Plots_Erstellen(einstellungen=einstellungen, gesamtbodendaten=gesamtbodendaten, indizes=indizes)
   #
   print('Beende MPO nach ' + str(time.time()-startzeit) + 's')
#


# -------------------------------------------------------------------------------------------------
import sys


if (sys.version_info[0] < 3):
   print('MPO benötigt mindestens Python3')
else:
   if (__name__ == '__main__'):
      main(sys.argv[1:])
   else:
      main(sys.argv[1:])
#

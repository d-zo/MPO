# -*- coding: utf-8 -*-
"""
hilfen.py   v0.4
2022-12 Dominik Zobel
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


# -------------------------------------------------------------------------------------------------
def Runden_Auf_Signifikante_Stellen(wert, stellen=6):
   """Runde den uebergebenen Wert auf die maximal definierten stellen.
   """
   # Angelehnt an https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python
   from math import floor, log10
   if (wert == 0):
      return 0.0
   else:
      return round(wert, -int(floor(log10(abs(wert)))) + (stellen - 1))
#


# -------------------------------------------------------------------------------------------------
def Daten_Reduzieren(daten, intervall=200):
   """Unterteile die uebergebenen daten (Liste an Listen) in Bloecke der Groesse intervall.
   Bestimme den Mittelwert jedes Blocks und gebe die Liste an Listen mit den Mittelwerten zurueck.
   """
   from math import ceil
   #
   werte_red = []
   iterationen = ceil(len(daten)/intervall)
   if (iterationen == 0):
      return None
   #
   laenge = intervall
   breite = len(daten[0])
   min_idx = 0
   for idx_it in range(iterationen):
      max_idx = (idx_it+1)*intervall
      if (idx_it == iterationen-1):
         max_idx = len(daten)
         laenge = max_idx - idx_it*intervall
      #
      temp_red = []
      for idx_breite in range(breite):
         temp_red += [sum([x[idx_breite] for x in daten[min_idx:max_idx]])/laenge]
      #
      werte_red += [temp_red]
      min_idx = max_idx
   #
   return werte_red
#


# -------------------------------------------------------------------------------------------------
def LinearInterpoliertenIndexUndFaktor(vergleichswert, vergleichswertliste):
   """Bestimme die Position von einem vergleichswert in einer (streng monoton steigenden)
   vergleichswertliste. Dabei wird linear zwischen Zwei Werten interpoliert. Gibt den Indiex des
   Wertes vor/zu dem vergleichswert und einen faktor zurueck [idx_davor, faktor].
   Fuer spaeteres Interpolieren kann folgender, linearer Zusammenhang genutzt werden:
   zielwert = zielvec[idx_davor] + faktor*(zielvec[idx_davor+1]-zielvec[idx_davor])
   """
   letzterIndex = len(vergleichswertliste) - 1
   for idx_wert, listenwert in enumerate(vergleichswertliste):
      if (listenwert == vergleichswert):
         if (idx_wert == letzterIndex):
            return [idx_wert-1, 1.0]
         else:
            return [idx_wert, 0.0]
      elif (listenwert > vergleichswert):
         if (idx_wert == 0):
            break
         #
         faktor = (vergleichswert-vergleichswertliste[idx_wert-1]) \
            / (vergleichswertliste[idx_wert]-vergleichswertliste[idx_wert-1])
         return [idx_wert-1, faktor]
   #
   print('# Warnung: Vergleichswert nicht in Liste gefunden (echt kleiner/groesser oder Liste unsortiert)')
   return [None, None]
#


# -------------------------------------------------------------------------------------------------
def Gleichmaessig_Unterteilte_Daten(x_min, x_max, num_werte, xdaten, extradaten=None):
   """Erwartet einen monoton steigenden Vektor xdaten (und optional weitere Vektoren gleicher Laenge
   in extradaten). Diese Funktion unterteilt xdaten in num_werte von x_min bis x_max und ermittelt
   durch lineare Interpolation die entsprechenden Werte. Fuer alle Vektoren im optionalen extradaten
   wird an den gleichen Stellen die gleiche lineare Interpolation durchgefuehrt. Gibt eine Liste
   mit den neuen Daten zurueck. Wenn xdaten nicht monoton steigend ist, x_min kleiner als der erste
   (d.h. kleinste) Wert in xdaten oder x_max groesser als der letzte (d.h. groesste) Wert in xdaten,
   dann wird eine Liste leerer Listen zurueckgegeben.
   """
   #
   xwerte = [x_min + (x_max - x_min)*x/(num_werte-1) for x in range(num_werte)]
   num_extra = 0
   if (extradaten is not None):
      num_extra = len(extradaten)
   #
   extrawerte = [[0 for ini in range(num_werte)] for x in range(num_extra)]
   #
   successful = True
   for idx_xwert, xwert in enumerate(xwerte):
      idx_davor, faktor = LinearInterpoliertenIndexUndFaktor(vergleichswert=xwert,
         vergleichswertliste=xdaten)
      if (idx_davor is None):
         return [[]] + [[] for x in range(num_extra)]
      #
      for idx_extra in range(num_extra):
         extrawerte[idx_extra][idx_xwert] = extradaten[idx_extra][idx_davor] + \
            faktor*(extradaten[idx_extra][idx_davor+1]-extradaten[idx_extra][idx_davor])
   #
   return [xwerte] + extrawerte
#


# -------------------------------------------------------------------------------------------------
def Daten_An_Stuetzstellen(xrefwerte, xdaten, extradaten):
   """Erwartet die monoton steigenden Vektoren xrefwerte und xdaten sowie weitere
   Vektoren mit der gleichen Laenge wie xdaten in extradaten. Diese Funktion unterteilt xdaten
   in die Anzahl an Werten von xrefwerte und interpoliert an den entsprechenden Stellen.
   Fuer alle Vektoren im optionalen extradaten wird an den gleichen Stellen die gleiche lineare
   Interpolation durchgefuehrt. Gibt eine Liste mit den neuen Daten zurueck. Wenn xdaten nicht
   monoton steigend ist, oder der erste Wert in xrefwerte kleiner als der erste (d.h. kleinste)
   Wert in xdaten oder der Endwert von xrefwerte groesser als der letzte (d.h. groesste) Wert in
   xdaten, dann wird eine Liste leerer Listen zurueckgegeben.
   """
   #
   num_extra = len(extradaten)
   extrawerte = [[0 for ini in range(len(xrefwerte))] for x in range(num_extra)]
   #
   successful = True
   for idx_xwert, xwert in enumerate(xrefwerte):
      idx_davor, faktor = LinearInterpoliertenIndexUndFaktor(vergleichswert=xwert,
         vergleichswertliste=xdaten)
      if (idx_davor is None):
         return [[] for x in range(num_extra)]
      #
      for idx_extra in range(num_extra):
         extrawerte[idx_extra][idx_xwert] = extradaten[idx_extra][idx_davor] + \
            faktor*(extradaten[idx_extra][idx_davor+1]-extradaten[idx_extra][idx_davor])
   #
   return extrawerte
#


# -------------------------------------------------------------------------------------------------
def prod(iterable):
   """Erstellt das Produkt aller Eintraege des uebergebenen iterables.
   """
   import operator
   from functools import reduce
   #
   return reduce(operator.mul, iterable, 1)
#


# -------------------------------------------------------------------------------------------------
def ZugriffEintrag(daten, zieleintrag):
   """Ermittelt in einer (ggfs. verschachtelten) dict-Struktur namens daten den Wert des
   geforderten zieleintrag. zieleintrag muss als Liste uebergeben werden. Gibt den wert des
   Zieleintrags bei erfolgreichen Auffinden des zieleintrags zurueck, sonst None.
   """
   if (len(zieleintrag) > 1):
      try:
         daten = daten[zieleintrag[0]]
      except:
         #print('# Warnung: Geforderter Eintrag enthaelt keinen Schluessel ' + zieleintrag[0])
         return None
      #
      return ZugriffEintrag(daten=daten, zieleintrag=zieleintrag[1:])
   else:
      try:
         rueckgabe = daten[zieleintrag[0]]
      except:
         #print('# Warnung: Geforderter Eintrag enthaelt keinen Schluessel ' + zieleintrag[0])
         return None
      #
      return rueckgabe
#

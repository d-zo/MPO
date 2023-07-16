# -*- coding: utf-8 -*-
"""
optionsverarbeitung.py   v0.5
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
def Hilfsausgabe(optionen):
   """Gib Benutzungshinweise in der Konsole aus.
   """
   print('Das Programm kann interaktiv oder mit allen folgenden Argumenten aufgerufen werden:')
   schalter = ''
   optionsuebersicht = '      mit'
   for option in optionen:
      schalter += ' -' + option[1] + '=[arg]'
      einrueckung = ' ' * (len(option[1]) + 5)
      for idx_unteropt, unteroption in enumerate(option[2]):
         if (idx_unteropt == 0):
            optionsuebersicht += '\n   -' + option[1] + '=' + unteroption[1] + ': '  \
               + unteroption[0]
         else:
            optionsuebersicht += '\n' + einrueckung + unteroption[1] + ': '  + unteroption[0]
   #
   print('python3 MPO.pyz' + schalter)
   print(optionsuebersicht)
   return None
#


# -------------------------------------------------------------------------------------------------
def _Uebergabewerte_Interpretieren(optionen, argumente):
   """Vergleiche die uebergebenen argumente, ob sie den in optionen definierten Erwartungswerten
   entsprechen. Es wird ein dict mit den eingelesenen Werten zurueckgegeben.
   Falls -h oder --help uebergeben wird oder die argumente nicht einwandfrei eingelesen werden
   können, wird die Hilfsausgabe aufgerufen. In diesem Fall wird None zurueckgegeben.
   """
   if ((len(argumente) == 1) and ((argumente[0] == '-h') or (argumente[0] == '--help'))):
      return Hilfsausgabe(optionen)
   #
   gesamtoptionen = dict()
   argument_bezeichner = [elem.split('=')[0][1:] for elem in argumente]
   for option in optionen:
      if (option[1] not in argument_bezeichner):
         print('# Abbruch: Argument -' + option[1] + ' nicht vorhanden')
         return Hilfsausgabe(optionen)
      else:
         unteroptionen = [unteropt[1] for unteropt in option[2]]
         for idx_arg, arg in enumerate(argument_bezeichner):
            if (option[1] == arg):
               wert_eingelesen = argumente[idx_arg].split('=')[1]
               if (wert_eingelesen not in unteroptionen):
                  print('# Abbruch: Ungueltiger Wert ' + wert_eingelesen + ' für Argument -' \
                     + option[1])
                  return Hilfsausgabe(optionen)
               #
               if (option[1] in gesamtoptionen):
                  print('# Warnung: Argument -' + option[1] + ' mehr als einmal uebergeben')
               #
               gesamtoptionen.update([(option[1], wert_eingelesen)])
   #
   # FIXME: Aktuell wird stillschweigend ignoriert, wenn zuviele Argumente eingelesen worden sind -> Warnung ausgeben
   return gesamtoptionen
#


# -------------------------------------------------------------------------------------------------
def _Auswahlliste_Zahleneingabe(beschreibung, optionen, max_iterationen=10):
   """Erstelle eine interaktive Auswahlliste mit der uebergebenen beschreibung. Unter optionen wird
   eine Liste mit bis zu neun Tupeln mit jeweils zwei Einträgen erwartet. Der erste Eintrag
   entspricht jeweils der angezeigten Option und der zweite Eintrag dem dazugehörigen Rückgabewert.
   Die Optionen werden der Reihe nach von 1 an durchnummeriert und durch eine interaktive Eingabe
   wird der entsprechende Wert ausgewählt. Falls 0 (Beenden) ausgewählt wird oder die Anzahl
   max_iterationen an zulässigen Versuchen überschritten wird, wird stattdessen None zurückgegeben.
   """
   idx_iteration = 0
   while True:
      idx_iteration += 1
      if (idx_iteration >= max_iterationen):
         print('# Abbruch: Zuviele Iterationen bei Verarbeitung der Zahleneingabe')
         return None
      #
      print(beschreibung)
      for idx, einzeloption in enumerate(optionen):
         print('      (' + str(idx+1) + ') ' + einzeloption[0])
      #
      print('      (0) Beenden')
      try:
         eingabewert = int(input('> '))
      except:
         # Integer ausserhalb der zulaessigen Optionen
         eingabewert = len(optionen)+1
      #
      if (eingabewert == 0):
         return None
      elif (eingabewert > 0) and (eingabewert <= len(optionen)):
         return optionen[eingabewert-1][1]
      else:
         print('Ungültige Eingabe\n')
#
   

# -------------------------------------------------------------------------------------------------
def _Interaktive_Optionsauswahl(optionen):
   """Lese die uebergebenen optionen über eine Benutzereingabe ein. Gibt ein dict mit den Werten
   aus optionen und der Benutzereingabe zuruck. Falls die Eingabe beendet worden ist, wird None
   zurueckgegeben.
   """
   gesamtoptionen = dict()
   for option in optionen:
      auswahl = _Auswahlliste_Zahleneingabe(beschreibung=option[0],
         optionen=option[2])
      if (auswahl is None):
         print('Beende ...')
         return None
      else:
         gesamtoptionen.update([(option[1], auswahl)])
   #
   return gesamtoptionen
#


# -------------------------------------------------------------------------------------------------
def Optionen_verarbeiten(argumente=[]):
   """Lese die uebergebenen argumente in eine Struktur von Optionen ein. Falls die Liste ungueltig
   ist, wird eine Hilfe ausgegeben und None zurueckgegeben. Falls eine leere Liste uebergeben wird,
   wird die Struktur von Optionen interaktiv ermittelt.
   """
   programmoptionen = [
      ['Was soll getan werden?', 'cmd',
         [['Alles abarbeiten', 'normal'],
         ['Liste mit Variationen erstellen', 'liste_erstellen'],
         ['Bestehende Liste mit Variationen nutzen', 'nutze_liste']]]]
   #
   if (len(argumente) == 0):
      optionen_formatiert = _Interaktive_Optionsauswahl(optionen=programmoptionen)
   else:
      optionen_formatiert = _Uebergabewerte_Interpretieren(optionen=programmoptionen,
         argumente=argumente)
   #
   return optionen_formatiert
#

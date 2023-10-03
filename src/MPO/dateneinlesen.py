# -*- coding: utf-8 -*-
"""
dateneinlesen.py   v0.3
2023-09 Dominik Zobel
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
def Existenz_Datei(dateiname):
    """Pruefe die Existenz einer Datei. Gibt True zurueck, falls die Datei vorhanden ist.
    """
    from pathlib import Path

    testdatei = Path(dateiname)
    if (testdatei.is_file()):
        return True
    else:
        return False



# -------------------------------------------------------------------------------------------------
def Datei_Einlesen(dateiname):
    """Lese die Datei namens dateiname ein und gib den eingelesenen Text zurueck.
    """
    inhalt_datei = ''
    with open(dateiname, 'r', encoding='utf-8') as eingabe:
        for zeile in eingabe:
            inhalt_datei += zeile

    return inhalt_datei



# -------------------------------------------------------------------------------------------------
def Datei_Schreiben(dateiname, inhalt):
    """Schreibe den uebergebenen inhalt in eine Datei namens dateiname.
    """
    with open(dateiname, 'w', encoding='utf-8') as ausgabe:
        ausgabe.write(inhalt)



# -------------------------------------------------------------------------------------------------
def Referenzdaten_Laden(einstellungen, str_versuch):
    from .hilfen import ZugriffEintrag

    refeintrag = einstellungen['Versuchsablauf'][str_versuch]['Referenzdaten']
    daten = JSONDateiEinlesen(dateiname=refeintrag['Datei'])
    inhalt = []
    for datenfeld in refeintrag['Daten']:
        temp_inhalt = ZugriffEintrag(daten=daten, zieleintrag=datenfeld)
        if (temp_inhalt is None):
            print('Fehler: Zugriff auf Referenzdaten ["' + '"]["'.join(datenfeld) + '"] aus Datei ' + refeintrag['Datei'] + ' fehlgeschlagen')
            return None

        inhalt += [temp_inhalt]

    return inhalt



# -------------------------------------------------------------------------------------------------
def Variationsdatei_Laden(dateiname):
    datenzeilen = []
    with open(dateiname, 'r') as eingabe:
        for zeile in eingabe:
            idx_kommentar = zeile.find('#')
            if (idx_kommentar > -1):
                zeile = zeile[:idx_kommentar]

            zeile = zeile.strip()
            if (len(zeile) == 0):
                continue

            datenzeilen += [zeile.split()]

    return datenzeilen



# -------------------------------------------------------------------------------------------------
def JSONDateiEinlesen(dateiname):
    """Lade eine JSON-formatierte Datei und gib die eingelesene Struktur zurueck.
    """
    import json

    eingelesen = None
    try:
        with open(dateiname, 'r', encoding='utf-8') as eingabe:
            eingelesen = json.load(eingabe)
    except FileNotFoundError:
        print('# Fehler: Datei ' + dateiname + ' konnte nicht gefunden/geoeffnet werden')
    except Exception as e:
        print('# Fehler: Datei ' + dateiname + ' konnte nicht eingelesen werden')
        print(e)

    return eingelesen



# -------------------------------------------------------------------------------------------------
def JSONDateiSpeichern(datensatz, dateiname):
    """Speichere die Stuktur datensatz als JSON-formatierte Datei namens dateiname.
    """
    import json

    class DatenstrukturEncoder(json.JSONEncoder):
        """Einfacher Encoder fuer Objekte der Datenstruktur-Klasse. Kovertiert Datenstruktur-Elemente
        in dicts und schreibt alle Listeneintraege in eine Zeile.
        """
        def default(self, o):
            return o.__dict__

        def iterencode(self, eintrag, _one_shot=False):
            listenstufe = 0
            for dumpstring in super().iterencode(eintrag, _one_shot=_one_shot):
                if (dumpstring[0] =='['):
                    listenstufe += 1
                    dumpstring = ''.join([teil.strip() for teil in dumpstring.split('\n')])

                elif (listenstufe > 0):
                    dumpstring = ' '.join([teil.strip() for teil in dumpstring.split('\n')])
                    if (dumpstring == ' '):
                        continue

                    if (dumpstring[-1] == ','):
                        dumpstring = dumpstring[:-1] + self.item_separator
                    elif (dumpstring[-1] == ':'):
                        dumpstring = dumpstring[:-1] + self.key_separator

                if (dumpstring[-1] == ']'):
                    listenstufe -= 1

                yield dumpstring

    with open(dateiname, 'w', encoding='utf-8') as ausgabe:
        json.dump(datensatz, ausgabe, cls=DatenstrukturEncoder, indent=3)



# -------------------------------------------------------------------------------------------------
def CSV_Ergebnisse_Einlesen(dateiname):
    """Lese die csv-Datei namens dateiname ein, die Leerzeichen als Trenner verwendet und keine
    Kopfzeile(n) hat. Gibt eine Liste an zeilenweisen Zahleneintraegen zurueck.
    """
    werte = []
    with open(dateiname, 'r', encoding='utf-8') as eingabe:
        for zeile in eingabe:
            werte += [[float(x) for x in zeile.split()]]

    return werte



# -------------------------------------------------------------------------------------------------
def Teildatei_Schreiben(neue_datei, datei, zeile_start=1, zeile_ende=1000000):
    """Lese den Inhalt aus datei von zeile_start bis zeile_ende (jeweils inklusive).
    Schreibe den eingelesenen Inhalt in neue_datei.
    """
    inhalt = ''
    with open(datei, 'r', encoding='utf-8') as eingabe:
        for idx_zeile, zeile in enumerate(eingabe):
            if (idx_zeile+1 < zeile_start):
                continue

            if (idx_zeile+1 > zeile_ende):
                break

            inhalt += zeile

    with open(neue_datei, 'w', encoding='utf-8') as ausgabe:
        ausgabe.write(inhalt)



# -------------------------------------------------------------------------------------------------
def Zeile_Muster(datei, muster):
    """Lese datei ein und untersuche jede Zeile nach muster. Gibt die (erste) Zeilennummer zurueck,
    die muster enthaelt oder None, falls keine Zeile das Muster enthaelt.
    """
    import os

    matzeile = None
    with open(datei, 'r', encoding='utf-8') as eingabe:
        for idx_zeile, zeile in enumerate(eingabe):
            if (muster in zeile):
                matzeile = idx_zeile+1
                break

    return matzeile



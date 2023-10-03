# -*- coding: utf-8 -*-
"""
programmsteuerung.py   v0.5
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
def Programmausfuehrung(befehl, bezugsordner='.', nachricht_abbruch='Undefinierter Fehler'):
    """Fuehrt mit dem uebergebenen befehl (als Liste) einen Systemaufruf durch. Wenn der Aufruf
    erfolgreich war, gibt die Funktion True zurueck, sonst False. Bei Misserfolg oder wenn der
    Rueckgabewert einer nicht erfolgreichen Ausfuehrung entspricht wird nachricht_abbruch ausgegeben.
    """
    import os
    import subprocess

    aktueller_ordner = os.path.abspath(os.curdir)
    os.chdir(bezugsordner)
    print('# ' + ' '.join(befehl))
    try:
        ergebnis = subprocess.run(befehl, shell=False, check=True)
    except subprocess.CalledProcessError:
        print('# Abbruch: ' + nachricht_abbruch)
        os.chdir(aktueller_ordner)
        return False
    except:
        print('# Fehler: ' + nachricht_abbruch)
        os.chdir(aktueller_ordner)
        return False

    if (ergebnis.returncode == 0):
        os.chdir(aktueller_ordner)
        return True
    else:
        print('# Abbruch: Rueckgabewert ungleich Null')
        os.chdir(aktueller_ordner)
        return False



# -------------------------------------------------------------------------------------------------
def _Simulation_und_Differenz(dateiname, args_davor, args_danach, eintragsliste, einstellungen,
    str_versuch, idx_zeile, vergleichsdaten, arbeitsverzeichnis, rueckgabemanager):
    """Diese Funktion uebernimmt saemtliche Variablen, um ggfs. parallel verschiedene Varianten zu
    berechnen und die Differenz zu vergleichsdaten zu bestimmen. Typischerweise sollten sich fuer
    parallele Prozesse/Aufrufe nur idx_zeile und eintrag voneinander unterscheiden. Der
    rueckgabemanager sammelt die Rueckgabewerte aller parallelen Prozesse zum Weiterverarbeiten.
    """
    import os
    from shutil import copy
    import tempfile
    from .dateneinlesen import Datei_Schreiben
    from .abweichung import Berechnung_Differenzen

    os.chdir(arbeitsverzeichnis)

    for idx_eintrag, eintrag in enumerate(eintragsliste):
        ausgabedatei = str_versuch + '_' + dateiname + '_' + str(idx_zeile+idx_eintrag).zfill(6) + '.csv'

        if (not Programmausfuehrung(befehl=['./' + dateiname, *args_davor, *eintrag, *args_danach, ausgabedatei], bezugsordner='.',
            nachricht_abbruch='Ausfuehren des Fortran-Programms fehlgeschlagen')):
            rueckgabemanager[idx_zeile+idx_eintrag] = '-1.0'
            continue

        abweichungen = Berechnung_Differenzen(einstellungen=einstellungen, vergleichsdaten=vergleichsdaten,
            str_versuch=str_versuch, datei=arbeitsverzeichnis + os.sep + ausgabedatei)

        rueckgabemanager[idx_zeile+idx_eintrag] = ', '.join([str(x) for x in abweichungen])



# -------------------------------------------------------------------------------------------------
def Berechne_Variationen(einstellungen, vergleichsdaten, str_versuch):
    """Fuehre die Simulationen aller zuvor vorbereiteten Variationen durch und speichere die
    Ergebnisse ab.
    """
    import os
    import time
    import multiprocessing as mp
    from .dateneinlesen import Datei_Einlesen, Variationsdatei_Laden

    # Beschraenke die Anzahl parallel ausgefuehrter Prozesse anhand der verfuegbaren Threads
    mp_gleichzeitig = max(mp.cpu_count()-1, 1)

    mp_manager = mp.Manager()
    rueckgabemanager = mp_manager.dict()
    mp_prozesse = []

    aktueller_ordner = os.path.abspath(os.curdir)
    arbeitsverzeichnis = einstellungen['Arbeitsverzeichnis'] + os.sep
    os.chdir(arbeitsverzeichnis)

    progeinstellungen = einstellungen['Versuchsablauf'][str_versuch]['Berechnungsprogramm']
    dateiname = progeinstellungen['Name']
    args_davor = progeinstellungen['zus. Argumente Start']
    args_danach = progeinstellungen['zus. Argumente Ende']

    abweichungsliste = []
    starttime = time.time()
    eingabeliste = Variationsdatei_Laden(dateiname=einstellungen['Ausgabedatei_Variationen'])

    print('\n# --- Anfang Multiprocessing Output (nutze ' + str(mp_gleichzeitig) + ' Threads) ---')
    # Teile die Liste an Arbeitspaketen (Eintraegen in eingabeliste) gleichmaessig auf die
    # verfuegbaren Threads auf
    num_arbeiten = len(eingabeliste)
    einzelarbeiten = num_arbeiten//mp_gleichzeitig
    num_extraarbeit = num_arbeiten % mp_gleichzeitig
    idx_ende = 0
    for idx_prozess in range(mp_gleichzeitig):
        idx_start = idx_ende
        idx_ende = idx_start + einzelarbeiten
        if (idx_prozess < num_extraarbeit):
            idx_ende += 1

        sp_prozess = mp.Process(target=_Simulation_und_Differenz, args=(dateiname, \
            args_davor, args_danach, eingabeliste[idx_start:idx_ende], einstellungen, \
            str_versuch, idx_start, vergleichsdaten, os.path.abspath(os.curdir), \
            rueckgabemanager))
        mp_prozesse.append(sp_prozess)
        sp_prozess.start()

    for prozess in mp_prozesse:
        prozess.join()

    print('# --- Ende Multiprocessing Output ---\n')
    abweichungsliste = [rueckgabemanager[schluessel] for schluessel in range(len(eingabeliste))]

    print('# Untersuchung der ' + str(len(eingabeliste)) + ' Variationen wurde abgeschlossen in: ' \
        + str(time.time()-starttime) + 's')

    with open(str_versuch + '_' + einstellungen['Ausgabedatei_Differenzen'], 'w', encoding='utf-8') as ausgabe:
        ausgabe.write('\n'.join(abweichungsliste))

    os.chdir(aktueller_ordner)



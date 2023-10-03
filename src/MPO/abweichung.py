# -*- coding: utf-8 -*-
"""
abweichung.py   v0.3
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
def _Unterschied_Gleichartiger_Vektoren(daten, refdaten, methode, skalierung=1.0):
    """Diese Funktion erwartet zwei gleichlange Vektoren, die deren Werte jeweils miteinander
    vergleichbar sind (bspw. an gleichen Punkten ausgewertet, am besten auch in konstanten
    Abstaenden). Daraufhin kann fuer die gewaehlte methode ein Wert fuer den Unterschied der beiden
    Vektoren ermittelt werden.
    """
    if (methode == 'fehlerquadrate'):
        unterschied = [((daten[idx] - refdaten[idx])/skalierung)**2 for idx in range(len(daten))]
    elif (methode == 'differenzflaeche'):
        #   + --- +
        #           `.
        #             `.                . o  b: refdaten
        #               + --- +   . o ´
        #   o .             . o ´.
        #       ` o-----o ´       `.
        #                           + --- +  a: daten
        #
        #   |     |     |     |     |     |
        #  a>b   a>b   a>b   a>b   b>a   b>a
        #      2     2     2     1     0
        unterschied = [0.0]
        for idx in range(len(daten)-1):
            refkleiner = 0
            if (daten[idx] > refdaten[idx]):
                refkleiner += 1

            if (daten[idx+1] > refdaten[idx+1]):
                refkleiner += 1

            if (refkleiner == 1):   # Ueberschlagenes Trapez (Hoehe 1)
                unterschied += [((daten[idx] - refdaten[idx])**2 + (daten[idx+1] - refdaten[idx+1])**2) \
                    / (2.0*skalierung*(abs(daten[idx] - refdaten[idx]) + abs(daten[idx+1] - refdaten[idx+1])))]
            else:                   # Normales Trapez (Hoehe 1)
                unterschied += [abs((daten[idx] - refdaten[idx]) + (daten[idx+1] - refdaten[idx+1]))/(2.0*skalierung)]
    else:
        # Betrags-Methode, wenn 'betrag' oder ungueltige Eingabe
        unterschied = [abs(daten[idx] - refdaten[idx])/skalierung for idx in range(len(daten))]

    #print('skal=' + str(skalierung) + '; vgl = (' + '), ('.join([str(w) + ': ' + str(x) + ', ' + str(y) + ' -> ' + str(z) \
    #   for w, x, y, z in zip(range(len(refdaten)), refdaten, daten, unterschied)]) + ')')
    return unterschied



# -------------------------------------------------------------------------------------------------
def Berechnung_Differenzen(einstellungen, vergleichsdaten, str_versuch, datei):
    """Lese die Ergebnisse aus datei ein und extrahiere die Daten an den ausgewaehlten Stuetzstellen,
    wie sie in einstellungen definiert sind. Bestimme den Unterschied zu den vergleichsdaten, die
    an den gleichen Stuetzstellen ausgewertet sind bzw. sein sollten.
    """
    from .dateneinlesen import CSV_Ergebnisse_Einlesen
    from .hilfen import Daten_An_Stuetzstellen

    simulationsergebnisse = CSV_Ergebnisse_Einlesen(dateiname=datei)
    xrefwerte = einstellungen['Versuchsablauf'][str_versuch]['Referenzdaten']['Relevante x-Werte']
    num_werte = len(xrefwerte)
    xsim = [x[0] for x in simulationsergebnisse]
    simdaten = []
    for idx_sim in range(len(simulationsergebnisse[0])-1):
        simdaten += [[x[idx_sim+1] for x in simulationsergebnisse]]

    simwerte = Daten_An_Stuetzstellen(xrefwerte=xrefwerte, xdaten=xsim, extradaten=simdaten)
    if (simwerte[0] == []):
        print('# Warnung: Ungueltige/nicht ausreichend Werte in den Simulationsdaten')
        if (xwerte != []):
            return [-1.0, xsim[0], xsim[-1]]
        else:
            return [-1.0]

    # Mit der ausgewaehlten Skalierung wird sozusagen die optische Uebereinstimmung bewertet.
    # In einem Plot der Referenzdaten entsprechen die Grenzen der vertikalen Achse dem Minimum/Maximum
    # der Referenzdaten und sind auf 1 skaliert. Dann wird bewertet, wie weit die restlichen Daten
    # mit dieser Skalierung von den Referenzdaten entfernt sind.
    methode = einstellungen['Fehlerbestimmungsmethode']
    refwerte = vergleichsdaten[1:]
    differenzen = [0 for x in range(num_werte)]
    for idx_wert in range(len(simwerte)):
        skalierung = max(refwerte[idx_wert]) - min(refwerte[idx_wert])
        temp_differenzen = _Unterschied_Gleichartiger_Vektoren(daten=simwerte[idx_wert],
            skalierung=skalierung, refdaten=refwerte[idx_wert], methode=methode)
        differenzen = [differenzen[idx] + temp_differenzen[idx] for idx in range(num_werte)]

    return differenzen



# -------------------------------------------------------------------------------------------------
def Bodendaten_Und_Vergleichsdaten(einstellungen, str_versuch):
    """Extrahiere aus den uebergebenen bodendaten die relevanten Versuchsdaten fuer str_versuch
    des Versuchsablaufs und unterteile die Daten in die angegebene Anzahl an (gleichverteilten)
    Werten. Sofern erfolgreich werden die Versuchsdaten und Informationen ueber einzelnen Werte
    als dict zurueckgegeben, ansonsten None.
    """
    from .hilfen import ZugriffEintrag, Daten_An_Stuetzstellen
    from .dateneinlesen import Referenzdaten_Laden

    bodendaten = Referenzdaten_Laden(einstellungen=einstellungen, str_versuch=str_versuch)
    if (bodendaten is None):
        return [None, None]

    xdaten = bodendaten[0]
    extradaten = bodendaten[1:]

    xrefwerte = einstellungen['Versuchsablauf'][str_versuch]['Referenzdaten']['Relevante x-Werte']

    # FIXME xdaten robust auf gueltiges Intervall beschraenken und monoton steigende Daten pruefen
    idx_start = -1
    idx_end = -1
    idx_refwert = 0
    for idx_xwert, xwert in enumerate(xdaten):
        if (xwert >= xrefwerte[idx_refwert]):
            if (idx_refwert == len(xrefwerte)-1):
                idx_end = idx_xwert
                break

            if (idx_start == -1):
                idx_start = max(0, idx_xwert-1)

            idx_refwert += 1

    if ((idx_start == -1) or (idx_end == -1)):
        print('# Abbruch: Es konnte kein gueltiges Intervall aus den x-Werten extrahiert werden')
        return [None, None]

    refdaten = Daten_An_Stuetzstellen(xrefwerte=xrefwerte, xdaten=xdaten[idx_start:idx_end+1],
        extradaten=[x[idx_start:idx_end+1] for x in extradaten])

    return [bodendaten, [xrefwerte] + refdaten]



# -------------------------------------------------------------------------------------------------
def Bewerte_Ergebnisse(einstellungen):
    """Bewerte alle Ergebnisse, die im Rahmen des Versuchsablaufs in die entsprechenden
    Ausgabedateien der Differenzen geschrieben wurden. Gibt eine nach der Bewertung der Ergebnisse
    (absteigend) sortierte Liste mit den Indizes der jeweiligen Variation zurueck oder eine leere
    Liste, falls kein (brauchbares) Ergebnis vorhanden ist.
    """
    import os
    from .dateneinlesen import Variationsdatei_Laden
    from .versuchsliste import Ermittle_Max_Variationen

    aktueller_ordner = os.path.abspath(os.curdir)
    os.chdir(einstellungen['Arbeitsverzeichnis'])

    variationswerte = Variationsdatei_Laden(dateiname=einstellungen['Ausgabedatei_Variationen'])
    anzahl_untersuchungen = len(variationswerte)

    gesamtwerte = [[0.0, x] for x in range(anzahl_untersuchungen)]
    disqualifiziert = [False for x in range(anzahl_untersuchungen)]

    num_zeilen = 0
    # Kann in beliebiger Reihenfolge durchgefuehrt werden
    for idx_schluessel, schluessel in enumerate(einstellungen['Versuchsablauf'].keys()):
        diff_datei = schluessel + '_' + einstellungen['Ausgabedatei_Differenzen']
        gewichtung = einstellungen['Versuchsablauf'][schluessel]['Gewichtungsfaktor']
        with open(diff_datei, 'r', encoding='utf-8') as eingabe:
            for idx_zeile, zeile in enumerate(eingabe):
                if (idx_schluessel == 0):
                    num_zeilen += 1

                eintraege = zeile.split(',')
                if (len(eintraege) <= 3):
                    # Irgendetwas ist schief gelaufen bei der Berechnung und es sind keine Daten verfuegbar
                    # Zaehle einen grossen Offset dazu, damit diese Daten auf jeden Fall ignoriert werden
                    disqualifiziert[idx_zeile] = True
                    gesamtwerte[idx_zeile][0] += 10000.0
                    continue

                gesamtwerte[idx_zeile][0] += sum([float(x) for x in eintraege])/len(eintraege)

    gesamtwerte = gesamtwerte[:num_zeilen]
    disqualifiziert = disqualifiziert[:num_zeilen]
    gesamtwerte.sort(key=lambda z: z[0])

    indizes_beste_ergebnisse = []
    print('# Die besten Bewertungen\n')
    with open(einstellungen['Ausgabedatei_Bewertung'], 'w', encoding='utf-8') as ausgabe:
        for idx in range(num_zeilen):
            idx_daten = gesamtwerte[idx][1]
            textzeile = '{:12.5f} ({:08d}): {}'.format(gesamtwerte[idx][0], idx_daten, ', '.join(variationswerte[idx_daten]))
            indizes_beste_ergebnisse += [idx_daten]
            ausgabe.write(textzeile + '\n')

            if (idx < 10):
                print(textzeile)

    print('')
    os.chdir(aktueller_ordner)
    return indizes_beste_ergebnisse



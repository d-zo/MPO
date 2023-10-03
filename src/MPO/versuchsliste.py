# -*- coding: utf-8 -*-
"""
versuchsliste.py   v0.4
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
def _Naechsten_Eintrag_Ermitteln(auswahlverfahren, index, variationen):
    """Waehle aus einer Liste mit der Anzahl variationen fuer verschiedene Eintraege den naechsten
    Eintrag aus. Je nach gewaehltem auswahlverfahren wird eine zufaellige Kombination erzeugt
    (monte_carlo) oder anhand des uebergebenen index ein Eintrag ermittelt (vollstaendig).
    """
    if (auswahlverfahren == 'monte_carlo'):
        import random

        naechste_variation = [round((x+1)*random.random() - 0.5) for x in variationen]

    else:
        if (auswahlverfahren != 'vollstaendig'):
            print('# Abbruch: Auswahlverfahren unbekannt - nehme vollstaendig an')

        # Wichtig: Er muss vorher sichergestellt werden, dass es sich bei einer vollstaendigen Auswahl
        #          auch tatsaechlich nur um eine handhabbare Menge an Variationen handelt
        naechste_variation = [0 for x in variationen]
        temp_idx = index
        for idx in range(len(variationen)):
            refeintrag = variationen[-(idx+1)] + 1
            temp_eintrag = temp_idx % refeintrag
            naechste_variation[-(idx+1)] = temp_eintrag
            temp_idx = (temp_idx-temp_eintrag) // refeintrag

    return naechste_variation



# -------------------------------------------------------------------------------------------------
def _Schreibe_Variation_In_Datei(ausgabedatei, eintraege):
    """Schreibe die in eintraege uebergebenen Zahlenwerte als Fortran-Listenvariable in ausgabedatei.
    Dabei werden die Werte auf signifikante Stellen gerundet und als Double Precision deklariert.
    """
    from .hilfen import Runden_Auf_Signifikante_Stellen

    ausgabezeilen = ' '.join([str(Runden_Auf_Signifikante_Stellen(wert=x, stellen=6)) for x in eintraege])
    with open(ausgabedatei, 'a', encoding='utf-8') as ausgabe:
        ausgabe.write(ausgabezeilen + '\n')



# -------------------------------------------------------------------------------------------------
def Ermittle_Max_Variationen(einstellungen):
    """Ermittle die notwendigen Variationen anhand der in einstellungen ausgewaehlten
    Auswahlverfahren/max. Variationen.
    """
    from .hilfen import prod

    anzahl_untersuchungen = einstellungen['max. Variationen']
    if (einstellungen['Auswahlverfahren'] == 'vollstaendig'):
        variationen = einstellungen['Optimierungsraum']['Variationen']
        anzahl_varianten = prod([x+1 for x in variationen])
        if (anzahl_varianten > anzahl_untersuchungen):
            print('Abbruch: Die erforderlichen ' + str(anzahl_varianten) \
                + ' Operationen liegen ueber dem definierten Maximum von ' \
                + str(einstellungen['max. Variationen']) + '.')
            print('         Eventuell ein anderes Auswahlverfahren oder ein groesseres Maximum waehlen')
            return None
        else:
            anzahl_untersuchungen = anzahl_varianten
            print('# Es werden ' + str(anzahl_varianten) + ' Operationen mit dem ' \
                + 'vollstaendigen Auswahlverfahren durchgefuehrt')
            anzahl_untersuchungen = anzahl_varianten
    elif (einstellungen['Auswahlverfahren'] == 'monte_carlo'):
        print('# Es werden ' + str(anzahl_untersuchungen) + ' Operationen mit zufaelliger Kombination ' \
            + '(Monte-Carlo-Verfahren) durchgefuehrt')

    return anzahl_untersuchungen



# -------------------------------------------------------------------------------------------------
def _Bedingungen_Erfuellt(einstellungen, eintraege):
    epsilon = 1e-9
    bezeichnungen = einstellungen['Optimierungsraum']['Bezeichnungen']
    bedingungen = einstellungen['Optimierungsraum']['Bedingungen']
    num_erfolg = 0
    is_invalid = False
    for bedingung in bedingungen:
        if (len(bedingung) != 3):
            print('MPO: Bedingung muss Bezeichner, Vergleichsoperator, Bezeichner sein')
            is_invalid = True
            break

        vergleichsoperator = bedingung[1]
        if (vergleichsoperator not in ['>', '>=', '==', '<=', '<']):
            print('MPO: Vergleichsoperator der Bedingung muss einer der folgenden sein: ">", ">=", "==", "<=", oder "<"')
            is_invalid = True
            break

        try:
            first = eintraege[bezeichnungen.index(bedingung[0])]
            second = eintraege[bezeichnungen.index(bedingung[2])]
        except:
            print('MPO: Bezeichner einer Bedingung müssen mit einem Eintrag aus "Bezeichnungen" übereinstimmen')
            is_invalid = True
            break

        #print('Checking ' + ''.join(bedingung) + ' with content ' + str(first) + vergleichsoperator + str(second))
        if ((vergleichsoperator == '>') and (first > second+epsilon)):
            num_erfolg += 1
        elif ((vergleichsoperator == '>=') and (first >= second)):
            num_erfolg += 1
        elif ((vergleichsoperator == '==') and (first == second)):
            num_erfolg += 1
        elif ((vergleichsoperator == '<=') and (first <= second)):
            num_erfolg += 1
        elif ((vergleichsoperator == '<') and (first < second-epsilon)):
            num_erfolg += 1
        #else:
        #   print('Condition not fulfilled')

    if (num_erfolg == len(bedingungen)):
        return [is_invalid, True]
    else:
        return [is_invalid, False]



# -------------------------------------------------------------------------------------------------
def _Versuchsliste_Parameter(ausgabedatei, einstellungen, anzahl_untersuchungen):
    """Schreibe anzahl_untersuchungen Parameter-Eintraege in die ausgabedatei. Die Parameter werden
    anhand der einstellungen variiert und die fertigen Eintraege koennen als Eingangsdaten fuer
    anschliessende Fortran-Untersuchungen genutzt werden.
    """
    from .dateneinlesen import Existenz_Datei

    min_eintraege = einstellungen['Optimierungsraum']['Werte (min)']
    max_eintraege = einstellungen['Optimierungsraum']['Werte (max)']
    variationen = einstellungen['Optimierungsraum']['Variationen']

    offsets = [max_eintraege[idx] - min_eintraege[idx] for idx in range(len(min_eintraege))]
    gewichtung = [0.0 for x in range(len(min_eintraege))]

    for idx_variation in range(anzahl_untersuchungen):
        naechste_variation = _Naechsten_Eintrag_Ermitteln(auswahlverfahren=einstellungen['Auswahlverfahren'],
            index=idx_variation, variationen=variationen)
        for idx in range(len(variationen)):
            if (variationen[idx] == 0):
                continue
            else:
                gewichtung[idx] = float(naechste_variation[idx])/float(variationen[idx])

        eintraege = [min_eintraege[idx] + offsets[idx]*gewichtung[idx] for idx in range(len(min_eintraege))]
        is_invalid, erfuellt = _Bedingungen_Erfuellt(einstellungen=einstellungen, eintraege=eintraege)
        if (is_invalid):
            return False
        elif (erfuellt):
            _Schreibe_Variation_In_Datei(ausgabedatei=ausgabedatei, eintraege=eintraege)

    # Return false if nothing was written and the file does not exist
    if (not Existenz_Datei(dateiname=ausgabedatei)):
        return False
    else:
        return True



# -------------------------------------------------------------------------------------------------
def Versuchsliste_Erstellen_Und_Speichern(einstellungen):
    """Erstelle eine Liste in der Datei einstellungen['Ausgabedatei_Variationen'], in der alle
    gewuenschten Parametervariationen gespeichert sind. Diese Datei kann anschliessend iterativ
    abgearbeitet werden.
    """
    import os
    from .dateneinlesen import Existenz_Datei

    ausgabedatei = einstellungen['Arbeitsverzeichnis'] + os.sep \
        + einstellungen['Ausgabedatei_Variationen']

    if (Existenz_Datei(dateiname=ausgabedatei)):
        os.remove(ausgabedatei)

    anzahl_untersuchungen = Ermittle_Max_Variationen(einstellungen=einstellungen)
    if (anzahl_untersuchungen is None):
        return False

    return _Versuchsliste_Parameter(ausgabedatei=ausgabedatei, einstellungen=einstellungen,
        anzahl_untersuchungen=anzahl_untersuchungen)



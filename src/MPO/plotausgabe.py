# -*- coding: utf-8 -*-
"""
plotausgabe.py   v0.2
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


# -------------------------------------------------------------------------------------------------
def PlotVorbereiten(plotbreite, plothoehe, breite_beschriftung_links=1.6,
   hoehe_beschriftung_unten=1.0, abstand_rechts=0.4, abstand_oben=0.2):
   """Bereitet einen Plot mit den standardmaessig hinterlegten Abstaenden/Bezugswerten vor.
   Fuer ein einheitliches Aussehen sollte diese Funktion angepasst und von allen Plotskripten
   aufgerufen werden (Customplot ruft diese Funktion intern auf).
   """
   from matplotlib import pyplot
   #
   # Fixwerte
   dpi = 300
   inch = 2.54; # [cm]
   #
   fig = pyplot.figure(figsize=(plotbreite/inch, plothoehe/inch), dpi=dpi)
   ax = pyplot.axes()
   axoffset = [breite_beschriftung_links/plotbreite, hoehe_beschriftung_unten/plothoehe]
   axsize = [1.0-(breite_beschriftung_links+abstand_rechts)/plotbreite,
             1.0-(hoehe_beschriftung_unten+abstand_oben)/plothoehe]
   ax.set_position([axoffset[0], axoffset[1], axsize[0], axsize[1]])
   #
   return [pyplot, fig, ax]
#


# -------------------------------------------------------------------------------------------------
def Plots_Erstellen(einstellungen, gesamtbodendaten, indizes):
   """Lese alle Ergebnisdateien des Versuchsablaufs aus einstellungen mit den uebergebenen indizes
   ein und plotte die besten Ergebnisse fuer jede Variation.
   """
   #
   # Entsprechendes Backend auswaehlen, u nicht-interaktive Plots zu ermoeglichen
   import matplotlib
   #
   matplotlib.use('Agg')
   #
   from matplotlib import pyplot
   from .dateneinlesen import JSONDateiEinlesen, CSV_Ergebnisse_Einlesen
   from .hilfen import Daten_Reduzieren
   #
   pyplot, fig1, ax1 = PlotVorbereiten(plotbreite=8.0, plothoehe=7.0)
   pyplot_b, fig2, ax2 = PlotVorbereiten(plotbreite=8.0, plothoehe=7.0)
   #
   num_plots_legende, num_plots = einstellungen['Plot Kurven']
   #
   import os
   aktueller_ordner = os.path.abspath(os.curdir)
   arbeitsverzeichnis = einstellungen['Arbeitsverzeichnis'] + os.sep
   os.chdir(arbeitsverzeichnis)
   for idx_ref, str_versuch in enumerate(einstellungen['Versuchsablauf'].keys()):
      bodendaten = gesamtbodendaten[idx_ref]
      versuchsdaten = einstellungen['Versuchsablauf'][str_versuch]
      basisdatei = str_versuch + '_' + einstellungen['Versuchsablauf'][str_versuch]['Berechnungsprogramm']['Name']
      #
      # FIXME: Should be agnostic of test (oedo, triax, whatever) and just plot over every used dimension
      if (len(bodendaten) == 2):
         versuchsart = 'Oedo'
      elif (len(bodendaten) == 3):
         versuchsart = 'Triax'
      else:
         versuchsart = None
      #
      x_referenz = bodendaten[0]
      y_referenz = bodendaten[1]
      if (versuchsart == 'Oedo'):
         labels = ['Spannung [kPa]', 'Porenzahl [-]']
      else:
         labels = ['Axiale Dehnung [\\%]', 'Volumetrische Dehnung [\\%]', 'Deviatorspannung [kPa]']
         z_referenz = bodendaten[2]
         ax1.set_xlim([0, 20.0])
         ax2.set_xlim([0, 20.0])
      #
      start_topplots = min(num_plots, len(indizes))-num_plots_legende
      for idx_plot, idx_versuch in enumerate(reversed(indizes[:num_plots])):
         num_versuch = str(idx_versuch).zfill(6)
         idx_leg = start_topplots + num_plots_legende - idx_plot
         werte = CSV_Ergebnisse_Einlesen(dateiname=basisdatei + '_' + num_versuch + '.csv')
         werte_red = Daten_Reduzieren(daten=werte, intervall=200)
         if (werte_red is None):
            continue
         #
         if (versuchsart == 'Oedo'):
            x_red = [x[0] for x in werte]
            y_red = [x[1] for x in werte]
            #
            if (idx_plot >= start_topplots):
               plotfarbe = pyplot.cm.viridis([1/num_plots_legende*(0.5 + idx_leg)])[0]
               label = 'Opt \\#' + str(idx_leg) + ': ' + str(idx_versuch)
               ax1.plot(x_red, y_red, color=plotfarbe, label=label, zorder=3)
            else:
               ax1.plot(x_red, y_red, color='#eeeeee', zorder=1)
         #
         else:
            x_red = [x[0] for x in werte]
            y_red = [x[1] for x in werte]
            z_red = [x[2] for x in werte]
            #
            if (idx_plot >= start_topplots):
               plotfarbe = pyplot.cm.viridis([1/num_plots_legende*(0.5 + idx_leg)])[0]
               label = 'Opt \\#' + str(idx_leg) + ': ' + str(idx_versuch)
               ax1.plot(x_red, y_red, color=plotfarbe, label=label, zorder=3)
               ax2.plot(x_red, z_red, color=plotfarbe, label=label, zorder=3)
            else:
               ax1.plot(x_red, y_red, color='#eeeeee', zorder=1)
               ax2.plot(x_red, z_red, color='#eeeeee', zorder=1)
      #
      zusatz = '_vol'
      if (versuchsart == 'Oedo'):
         zusatz = ''
         ax1.set_xscale('log')
      #
      ax1.plot(x_referenz, y_referenz, 'k--', zorder=2)
      #ax1.set_title(basisdatei)
      #ax1.grid(which='major', linestyle=':')
      ax1.grid(which='minor', color='#dddddd', linestyle=':')
      ax1.set_xlabel(labels[0])
      ax1.set_ylabel(labels[1])
      ax1.legend()
      # Reihenfolge der Eintraege korrigieren
      leg_handles, leg_labels = ax1.get_legend_handles_labels()
      ax1.legend(leg_handles[::-1], leg_labels[::-1])
      #
      fig1.savefig(basisdatei + zusatz + '.pdf')
      ax1.clear()
      #
      if (versuchsart == 'Triax'):
         zusatz = '_dev'
         ax2.plot(x_referenz, z_referenz, 'k--', zorder=2)
         #ax2.set_title(basisdatei)
         #ax2.grid(which='major', linestyle=':')
         ax2.grid(which='minor', color='#dddddd', linestyle=':')
         ax2.set_xlabel(labels[0])
         ax2.set_ylabel(labels[2])
         ax2.legend()
         # Reihenfolge der Eintraege korrigieren
         leg_handles, leg_labels = ax2.get_legend_handles_labels()
         ax2.legend(leg_handles[::-1], leg_labels[::-1])
         #
         fig2.savefig(basisdatei + zusatz + '.pdf')
         ax2.clear()
   #
   os.chdir(aktueller_ordner)
#


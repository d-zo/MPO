
MPO 0.4
======================

[MPO](https://github.com/d-zo/MPO)
can be used to optimize soil material parameters in a given range and find the best match
compared to a reference data set.
It was created at the Institute of Geotechnical Engineering
at the Hamburg University of Technology.


Installation
------------

MPO requires a Python 3.7+ environment and
the zipapp file can be run with Python.
Precompiled programs or a Fortran compiler and and a user routine with UMAT interface is needed
to compile the geotechnical laboratory tests
(xMat user routine and GNU and Intel Fortran compilers were used for testing).
Internally the libraries `subprocess` is used for system calls and
`multiprocessing` to execute computations in parallel.
Also [matplotlib](https://matplotlib.org/) is used for plotting.


Running the program
-------------------

In Linux the following commands can be used in a shell
(the first command has to be adjusted to point to the right directory).

```
cd /path/to/MPO
python3 MPO.pyz
```

In Windows a batch file can be created to provide access to MPO.
Therefore, the path to the Python interpreter and the path to MPO have to be
defined in the following code.

```
@echo off
pushd C:\path\to\MPO
C:\path\to\Python\python.exe C:\path\to\MPO\MPO.pyz
pause
```

MPO can be run interactively if called without any options (as shown above)
or with all of the following options as a batch run:

```
python3 MPO.pyz -cmd=[arg]
```

The arguments and their options are

 - `cmd` to specify which kind of operation MPO should perform
    - `normal`: Do a complete run of MPO
    - `liste_erstellen`: Only create a list of variations for further runs
    - `nutze_liste`: Run MPO based on a given list of variations

Since MPO was created alongside the xMat user routine (see <https://github.com/d-zo/xMat>),
this user routine can also be used to test MPO.

A simple function documentation (in german) created with pydoc can be found
[here](https://d-zo.github.io/MPO/MPO.html "MPO documentation").


Structure
---------

Using MPO requires certain files and folders.
Typically the zipapp `MPO.pyz` is used inside a prepared directory with the following structure

 - `workdir/`: An arbitrary named working directory with its name and containing all test programs specified in `einstellungen.json`.
   As an example the files `Umat_Oedo.f` and `Umat_Triax.f` are provided which have to be compiled with a user routine
   having a UMAT interface
 - `einstellungen.json`: JSON-file with all directly configurable settings for running the program
 - `MPO.pyz`: Main program as zipapp
 - `referenz.json`: An arbitrary named JSON-file with experiment reference data for each variant specified in `einstellungen.json`


At the moment MPO makes some implicit assumptions due to the was it was mainly used.
Although in general different kind of test programs can be used,
it is assumed that they perform either oedometric or triaxial tests right now.
Furthermore, oedometric tests are currently recognized by having two entries
and triaxial tests by having three.


**Structure of `referenz.json`**

Each set of reference data is supposed to comply with one of the following structures
with the exact names of the entries.
For oedometric tests

```
 "<unique-oedo-test-name>": {
  "Data": {
   "Spannung [kPa]": [...],
   "Porenzahl [-]": [...]
  }
```

and for triaxial tests

```
 "<unique-triax-test-name>": {
  "Data": {
   "Axiale Dehnung [%]": [...],
   "Deviatorspannung [kPa]": [...],
   "Volumetrische Dehnung [%]": [...]
  }
```


**Structure of `einstellungen.json`**

All relevant settings for running MPO are stored in `einstellungen.json`.
It is expected to have

 - `Arbeitsverzeichnis`: Name of the working directory relative to the current one. By default `workdir` is used here.
   All files within a run of MPO including the following three files are created inside this folder.
 - `Ausgabedatei_Variationen`: Name of the intermediate file containing all variations to be investigated.
 - `Ausgabedatei_Differenzen`: Name of the output file with the differences between the variations and the reference data.
 - `Ausgabedatei_Bewertung`: Name of the final output file with the overall ranking of the results.
 - `max. Variationen`: Maximum amount of calculations to perform. This is intended to be a safeguard against
   starting more calculations than intended or manageable in a given time frame.
 - `Plot Kurven` expects two values controlling the plot behaviour. The first number specifies
   how many of the best results should at most plotted and discriminated as colored and labelled lines.
   The second number controls how many results should be plotted as uniform gray background lines.
 - `Auswahlverfahren` controls which kind of selection procedure should be conducted. Accepts `vollstaendig`
   to perform all possible combinations defined in `Optimierungsraum` or `monte_carlo` to have as many
   randomly selected combinations of values in `Optimierungsraum` as defined in `max. Variationen`.
 - `Fehlerbestimmungsmethode` defines how the error between the reference data and the calculations should be computed.
   Valid options are `fehlerquadrate`, `differenzflaeche` and `betrag`.
   In all cases data is interpolated for reference data and calculated data at the same points along the x axis.
   Monotonically increasing data on this axis is assumed.
   Using `fehlerquadrate` the squares of the difference between each of those common points is calculated.
   `differenzflaeche` calculates the absolute area between two consecutive points from both data sets
   (also for flipped trapezoids when the lines for those points cross each other)
   and `betrag` determines the absolute difference of each set of points.
 - `Versuchsablauf` is a structure with at least one set of named data to test.
   For each named data, three entries are required: `Referenzdaten`, `Berechnungsprogramm` and `Gewichtungsfaktor`.
    - `Referenzdaten` specifies the name of the file with the reference data as `Datei`.
      The name within the structure to get the data as comma separated values in `Daten`.
      In the example for the oedometric test above this would be
      `[["<unique-oedo-test-name>", "Data", "Spannung [kPa]"], ["<unique-oedo-test-name>", "Data", Porenzahl [-]]]`.
      And a list of values called `Relevante x-Werte` which relates either to `Spannung [kPa]` for oedometric tests
      or `Axiale Dehnung [%]` for triaxial tests. The defined values are the common sampling points where
      the error between reference data and calculation is determined.
    - `Berechnungsprogramm` defines three values:
      `Name` is the name of the program to call for performing the calculations.
      Additionally to calling it, three sets of values are passed to the program:
      A set of values at the beginning `zus. Argumente Start`, the calculated material parameters within MPO
      and a set of values at the end `zus. Argumente Ende`.
    - `Gewichtungsfaktor` is a factor to multiply the results with when determining the overll result based
      on all tests

 - `Optimierungsraum`: Defines the start and end values as well as the amount of steps in between for each material parameter.
    - `Bezeichnungen` defines the name of each parameter. They should already be in the order in which they are passed to
      the calculation program and there are no restrictions on the actual names. They are used to associate the values
      clearly and be able to define conditions in `Bedingungen`.
    - `Bedingungen` allows to specify conditions in the form `["one variable name", "condition", "other variable name"]`
      where condition is one of `>`, `>=`, `==`, `<=`, or `<`. Only combinations with a valid condition will be considered,
      invalid ones will be skipped.
    - `Werte (min)` and `Werte (max)` define the minimum and maximum value of individual parameters.
    - `Variationen` determines how many values besides the minimum value will be used.
      Zero means that only the minimum value specified in `Werte (min)` will be used,
      one uses additionally the value stored in `Werte (max)`. Higher values use the n-1 equidistant sampling points
      between both values.


Every set of tests in `Versuchsablauf` is supposed to have a corresponding set of reference data in `referenz.json`
with the given structure.
Currently no tests are conducted on the structure/naming of the entries in `einstellungen.json`.
So if some needed value is missing or misspelled, the program will abort when it is trying to access it.



Contributing
------------

**Bug reports**

If you found a bug, make sure you can reproduce it with the latest version of MPO.
Please check that the expected results can actually be achieved by other means
and are not considered invalid operations due to problematic template files.
Please give detailed and reproducible instructions in your report including

 - the MPO version
 - the expected result
 - the result you received
 - the command(s) used as a _minimal working example_

Note: The bug should ideally be reproducible by the _minimal working example_ alone.
Please keep the example code as short as possible (minimal).


**Feature requests**

If you have an idea for a new feature, consider searching the
[open issues](https://github.com/d-zo/MPO/issues) and
[closed issues](https://github.com/d-zo/MPO/issues?q=is%3Aissue+is%3Aclosed) first.
Afterwards, please submit a report in the
[Issue tracker](https://github.com/d-zo/MPO/issues) explaining the feature and especially

 - why this feature would be useful (use cases)
 - what could possible drawbacks be (e.g. compatibility, dependencies, ...)



License
-------

MPO is released under the
[GPL](https://www.gnu.org/licenses/gpl-3.0.html "GNU General Public License"),
version 3 or greater (see als [LICENSE](https://github.com/d-zo/MPO/blob/master/LICENSE) file).
It is provided without any warranty.


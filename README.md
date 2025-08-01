# IAQP 62.1 Console Toolkit
This folder contains a small command-line tool that sizes outdoor airflow
(Voz) and calculates steady-state breathing-zone concentrations (Cbz) for
the 2022 IAQP procedure in ASHRAE 62.1.  Everything runs locally – no
external data files are required.

-----------------------------------------------------------------------
1. Folder contents
-----------------------------------------------------------------------
File                     | Purpose
-------------------------|-----------------------------------------------------------
mainIAQPconsole.py       | User-facing console app.  Parses CLI flags, performs all
                         | calculations, prints the tables.
mass_balance.py          | Table F-1 mass-balance equations for filter locations
                         | A and B (both VAV and constant-volume forms).
iaq_dictionaries.py      | Design limits, default outdoor concentrations, emission
                         | rates, VRP Table 6-1 data, mixture-group definitions.
air_cleaner.py           | Compound-specific cleaner efficiencies + lookup helper.
run.bat (optional)       | Example Windows batch that runs several scenarios.
output.txt (optional)    | Captured sample output produced by run.bat > output.txt.

-----------------------------------------------------------------------
2. Quick start
-----------------------------------------------------------------------
python mainIAQPconsole.py -occupancy "Classrooms (age 9 plus)" ^
       -area_ft2 950 -Recirc_CFM 50 -num_people 5 -loc B

The program prints:
* Scenario Summary
* Voz table
* Cbz table (includes % of design limit)
* Mixture sums
* Final airflow numbers

-----------------------------------------------------------------------
3. Command-line flags
-----------------------------------------------------------------------
(Only an area flag is mandatory; defaults are in **bold**.)

Flag            | Type   | Default | Meaning
--------------- | ------ | ------- | ---------------------------------------------
-occupancy      | str    | "Classrooms (age 9 plus)" | Must match a Table 6-1 name.
-area_m2        | float  | 90.0    | Floor area in square metres.
-area_ft2       | float  | –       | Floor area in square feet (converted).
-num_people     | int    | derived | Override head-count (else density × area).
-R              | float  | 0.0     | Recirculation ratio (fraction). Ignored if
                         |         | a recirculation airflow flag is supplied.
-Recirc_CFM     | float  | –       | Recirc airflow in CFM. Program back-calculates R.
-Recirc_CMH     | float  | –       | Same, in m³/h.
-Ef             | float  | **0.5** | Global cleaner efficiency. Use 0 to disable.
-Ez             | float  | **1.0** | Zone air-distribution effectiveness.
-safe_factor    | float≤1| **1.0** | Multiply every design limit by this factor.
-loc            | str    | **A**   | Filter location A or B (defaults to A).
-units          | str    | **BOTH**| Output units: CFM, CMH, or BOTH.

-----------------------------------------------------------------------
4. Batch runs and logging
-----------------------------------------------------------------------
Create a batch file (Windows example run.bat):

python mainIAQPconsole.py -occupancy "Office space" -area_ft2 500 -Recirc_CFM 100
python mainIAQPconsole.py -occupancy "Break rooms (General)" -area_ft2 300 -num_people 15 -Recirc_CFM 75

Run it and capture all console output:

run.bat > output.txt  2>&1

-----------------------------------------------------------------------
5. Extending the tool
-----------------------------------------------------------------------
* Cleaner efficiencies – edit air_cleaner.py.
* New compounds or occupancies – extend the dictionaries in
  iaq_dictionaries.py (design limits, outdoor levels, emission rates).
* New CLI flags – add parser.add_argument(...) lines in
  mainIAQPconsole.py and thread the values into the calculation blocks.

The code is plain Python 3 with no external packages – clone and run.

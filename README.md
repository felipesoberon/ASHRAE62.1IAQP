# IAQP 62.1 Console Toolkit

This folder contains a small command-line tool that sizes outdoor airflow
(Voz) and calculates steady-state breathing-zone concentrations (Cbz) for
the 2022 IAQP procedure in ASHRAE 62.1.  Everything runs locally – no
external data files are required.

-----------------------------------------------------------------------
## 1  Folder contents

| File                     | Purpose                                                       |
|--------------------------|---------------------------------------------------------------|
| mainIAQPconsole.py       | User-facing console app.  Parses CLI flags, performs all      |
|                          | calculations, prints the tables.                              |
| mass_balance.py          | Table F-1 mass-balance equations for filter positions A and B |
|                          | (both VAV and constant-volume forms).                         |
| iaq_dictionaries.py      | Design limits, default outdoor concentrations, emission       |
|                          | rates, VRP Table 6-1 data, mixture group definitions.         |
| air_cleaner.py           | Compound-specific cleaner efficiencies + lookup helper.       |
| run.bat (optional)       | Example Windows batch that runs several scenarios.            |
| output.txt (optional)    | Captured sample output produced by run.bat > output.txt.      |

-----------------------------------------------------------------------
## 2  Quick start

```bash
python mainIAQPconsole.py -occupancy "Classrooms (age 9 plus)" \
       -area_ft2 950 -Recirc_CFM 50 -num_people 5 -loc B

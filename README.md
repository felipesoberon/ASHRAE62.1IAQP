# IAQP 62.1 Console Toolkit

A minimalist command-line tool for sizing outdoor airflow (Voz) and computing steady-state breathing-zone concentrations (Cbz) using the Indoor Air Quality Procedure (IAQP) from ASHRAE 62.1-2022. Everything runs locally—no external packages required.

-------------------------------------------------------------------------------
1. Folder contents

| File                | Purpose                                                      |
|---------------------|--------------------------------------------------------------|
| mainIAQPconsole.py  | CLI front-end: parses flags, runs calculations, prints tables|
| mass_balance.py     | Table F-1 mass-balance formulas (filter at A or B, VAV/CV)   |
| iaq_dictionaries.py | Design limits, outdoor concs, emission rates, Table 6-1 data |
| air_cleaner.py      | Compound-specific cleaner efficiencies + lookup helper        |
| run.bat   (optional)| Example Windows batch to run scenarios                       |
| output.txt (optional)| Example output from `run.bat > output.txt`                  |

Only the first four files are required to run the tool.

-------------------------------------------------------------------------------
2. Quick start

```
python mainIAQPconsole.py -occupancy "Classrooms (age 9 plus)" -area_ft2 950 -Recirc_CFM 50 -num_people 5 -loc B
```

The program prints:

- Scenario summary
- Voz table
- Cbz table (includes % of design limit)
- Mixture exposure sums
- Final airflow line

-------------------------------------------------------------------------------
3. Command-line flags

At least one area flag is mandatory; all others have defaults.

| Flag          | Type    | Default                 | Description                                  |
|---------------|---------|-------------------------|----------------------------------------------|
| -occupancy    | str     | "Classrooms (age 9 plus)" | Must match a Table 6-1 name                  |
| -area_m2      | float   | —                       | Floor area in square metres                  |
| -area_ft2     | float   | 90.0 m2 equivalent      | Floor area in square feet (converted)        |
| -num_people   | int     | derived                 | Override head-count (else density × area)    |
| -R            | float   | 0.0                     | Recirc ratio (fraction). Ignored if airflow flag given |
| -Recirc_CFM   | float   | —                       | Recirc airflow in CFM. Program back-calculates R |
| -Recirc_CMH   | float   | —                       | Same, in m3/h                                |
| -Ef           | float   | 0.5                     | Global cleaner efficiency. 0 disables cleaner|
| -Ez           | float   | 1.0                     | Zone air-distribution effectiveness          |
| -safe_factor  | float   | 1.0 (≤1)                | Multiply each design limit by this factor    |
| -loc          | str     | A                       | Filter location A or B                       |
| -units        | str     | BOTH                    | Output units: CFM, CMH, or BOTH              |

-------------------------------------------------------------------------------
4. Batch runs and logging

Example Windows batch file (`run.bat`):

```
python mainIAQPconsole.py -occupancy "Office space" -area_ft2 500 -Recirc_CFM 100
python mainIAQPconsole.py -occupancy "Break rooms (General)" -area_ft2 300 -num_people 15 -Recirc_CFM 75
```

To run all scenarios and capture the output:

```
run.bat > output.txt 2>&1
```

-------------------------------------------------------------------------------
5. Extending the tool

- Edit `air_cleaner.py` for cleaner efficiencies.
- Add new compounds or occupancies in `iaq_dictionaries.py`.
- Add more CLI flags with `parser.add_argument(...)` in `mainIAQPconsole.py`.

This code is plain Python 3—no external libraries required.

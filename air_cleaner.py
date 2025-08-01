"""
air_cleaner.py

Default air-cleaner (filter) removal efficiencies for each IAQP 62.1 2022
design compound.  All efficiencies are fractions in the range 0-1.
"""

CLEANER_EFFICIENCY = {
    "acetaldehyde":          0.315,
    "acetone":               0.525,
    "benzene":               0.986,
    "dichloromethane":       0.398,
    "formaldehyde":          0.397,
    "naphthalene":           0.987,
    "phenol":                0.259,
    "tetrachloroethylene":   0.977,
    "toluene":               0.985,
    "1,1,1-trichloroethane": 0.41,
    "xylene, total":         0.981,
    "carbon monoxide":       0.007,
    "pm2.5":                 0.77,
    "ozone":                 0.985,
    "ammonia":               0.12,
}

def get_cleaner_efficiency(compound):
    """
    Return the default air-cleaner efficiency (fraction, 0-1) for a compound.
    Matching is case-insensitive; raises KeyError if not found.
    """
    return CLEANER_EFFICIENCY[compound.strip().lower()]